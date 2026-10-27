"""Private local conversation memory for GhostShell (Phase 5).

Provides lightweight, private, file-based persistence for conversation history
and user preferences using safe atomic JSON replacement.
Never stores environment variables, credentials, or full project directories.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final


DEFAULT_MAX_HISTORY_ENTRIES: Final[int] = 50
DEFAULT_CONTEXT_WINDOW_PAIRS: Final[int] = 3


@dataclass
class MemoryEntry:
    """Individual conversation turn stored in local memory.

    Attributes:
        timestamp: Unix epoch timestamp of interaction.
        role: Message author ('user' or 'assistant').
        content: Text content of the turn.
        metadata: Optional execution telemetry (tokens, latency, mode).
    """

    timestamp: float
    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class GhostMemory:
    """Private, local-first conversation memory manager.

    Maintains bounded conversation history and preferences in a configurable
    local directory. Supports atomic file writes, graceful corruption recovery,
    and a zero-persistence mode when disabled.
    """

    def __init__(
        self,
        data_dir: str | Path | None = None,
        enabled: bool = True,
        max_entries: int = DEFAULT_MAX_HISTORY_ENTRIES,
    ) -> None:
        """Initialize the local memory store.

        Args:
            data_dir: Target storage directory (defaults to ~/.ghostshell).
            enabled: If False, persistence is disabled and operates strictly in-memory.
            max_entries: Maximum number of conversation records retained.
        """
        self.enabled = enabled
        self.max_entries = max_entries

        if data_dir is not None:
            self.data_dir = Path(data_dir).expanduser().resolve()
        else:
            # Default to user home directory ~/.ghostshell
            self.data_dir = Path.home() / ".ghostshell"

        self.history_file = self.data_dir / "history.json"
        self.prefs_file = self.data_dir / "preferences.json"

        # Ephemeral memory buffer used when persistence is disabled or before flush
        self._in_memory_history: list[MemoryEntry] = []
        self._in_memory_prefs: dict[str, Any] = {}

        if self.enabled:
            self._ensure_directory()
            self._load_from_disk()

    def _ensure_directory(self) -> None:
        """Ensure the target local storage directory exists."""
        if not self.enabled:
            return
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Fallback to current working directory if home dir has restricted permissions
            self.data_dir = Path(".ghostshell_data").resolve()
            self.history_file = self.data_dir / "history.json"
            self.prefs_file = self.data_dir / "preferences.json"
            try:
                self.data_dir.mkdir(parents=True, exist_ok=True)
            except OSError:
                # If disk writes completely fail, run in-memory
                self.enabled = False

    def _load_from_disk(self) -> None:
        """Load history and preferences safely, recovering from corrupt files."""
        if not self.enabled:
            return

        # Load history
        if self.history_file.exists():
            try:
                content = self.history_file.read_text(encoding="utf-8", errors="replace")
                data = json.loads(content)
                if isinstance(data, list):
                    self._in_memory_history = [
                        MemoryEntry(
                            timestamp=item.get("timestamp", time.time()),
                            role=item.get("role", "unknown"),
                            content=item.get("content", ""),
                            metadata=item.get("metadata", {}),
                        )
                        for item in data
                        if isinstance(item, dict)
                    ]
            except (json.JSONDecodeError, OSError):
                # Corruption recovery: rename corrupt file to .bak and start fresh
                try:
                    bak_file = self.history_file.with_suffix(".json.corrupt.bak")
                    shutil.move(str(self.history_file), str(bak_file))
                except OSError:
                    pass
                self._in_memory_history = []

        # Load preferences
        if self.prefs_file.exists():
            try:
                content = self.prefs_file.read_text(encoding="utf-8", errors="replace")
                data = json.loads(content)
                if isinstance(data, dict):
                    self._in_memory_prefs = data
            except (json.JSONDecodeError, OSError):
                self._in_memory_prefs = {}

    def _atomic_write_json(self, target_path: Path, data: Any) -> bool:
        """Write JSON atomically via temporary file replacement.

        Prevents file truncation or corruption if interrupted mid-write.

        Args:
            target_path: Path to the destination file.
            data: Object to serialize.

        Returns:
            True on successful atomic flush, False on write failure.
        """
        if not self.enabled:
            return False

        try:
            self._ensure_directory()
            temp_file = target_path.with_suffix(f".tmp.{os.getpid()}")
            with open(temp_file, "w", encoding="utf-8", errors="replace") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename / replace
            os.replace(temp_file, target_path)
            return True
        except OSError:
            return False

    def record_turn(
        self,
        user_prompt: str,
        assistant_response: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a completed conversation turn (user prompt + assistant response).

        Args:
            user_prompt: Cleaned prompt text from user.
            assistant_response: Content returned to user.
            metadata: Diagnostic details (tokens, mode, latency).
        """
        now = time.time()
        meta = metadata or {}

        user_entry = MemoryEntry(timestamp=now, role="user", content=user_prompt)
        asst_entry = MemoryEntry(
            timestamp=now,
            role="assistant",
            content=assistant_response,
            metadata=meta,
        )

        self._in_memory_history.extend([user_entry, asst_entry])

        # Enforce maximum retention bounds (FIFO truncation)
        if len(self._in_memory_history) > self.max_entries:
            self._in_memory_history = self._in_memory_history[-self.max_entries :]

        if self.enabled:
            serializable = [asdict(e) for e in self._in_memory_history]
            self._atomic_write_json(self.history_file, serializable)

    def get_history(self, limit: int | None = None) -> list[MemoryEntry]:
        """Retrieve recent conversation entries.

        Args:
            limit: Maximum count of entries to return (default: all up to max_entries).

        Returns:
            List of MemoryEntry objects in chronological order.
        """
        if limit is None or limit >= len(self._in_memory_history):
            return list(self._in_memory_history)
        return self._in_memory_history[-limit:]

    def get_context_messages(
        self, max_pairs: int = DEFAULT_CONTEXT_WINDOW_PAIRS
    ) -> list[dict[str, str]]:
        """Extract a bounded list of recent message pairs for Gemma context.

        Args:
            max_pairs: Maximum number of user-assistant pairs to include.

        Returns:
            List of dicts with 'role' and 'content' formatted for chat completions.
        """
        if not self._in_memory_history or max_pairs <= 0:
            return []

        # Find the last N pairs (up to max_pairs * 2 entries)
        needed_entries = max_pairs * 2
        recent = self._in_memory_history[-needed_entries:]

        messages: list[dict[str, str]] = []
        for entry in recent:
            if entry.role in ("user", "assistant"):
                # Bound each context message to prevent runaway prompts
                bounded_content = entry.content[:600]
                messages.append({"role": entry.role, "content": bounded_content})
        return messages

    def clear(self) -> None:
        """Clear ephemeral history and delete the history file on disk."""
        self._in_memory_history.clear()
        if self.enabled and self.history_file.exists():
            try:
                self.history_file.unlink()
            except OSError:
                pass

    def forget(self) -> bool:
        """Completely purge all stored history and preferences from disk.

        Returns:
            True if purge completed successfully, False otherwise.
        """
        self._in_memory_history.clear()
        self._in_memory_prefs.clear()

        success = True
        if self.enabled:
            for f in (self.history_file, self.prefs_file):
                if f.exists():
                    try:
                        f.unlink()
                    except OSError:
                        success = False
        return success

    def set_preference(self, key: str, value: Any) -> None:
        """Save a user preference (e.g. active persona, theme).

        Args:
            key: Setting identifier.
            value: Setting value (must be JSON-serializable).
        """
        self._in_memory_prefs[key] = value
        if self.enabled:
            self._atomic_write_json(self.prefs_file, self._in_memory_prefs)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve a stored preference.

        Args:
            key: Setting identifier.
            default: Fallback value if setting is not present.

        Returns:
            Saved value or default.
        """
        return self._in_memory_prefs.get(key, default)

    def get_storage_diagnostics(self) -> dict[str, Any]:
        """Return diagnostic metadata regarding memory storage and privacy.

        Returns:
            Dictionary describing storage paths, counts, and security invariants.
        """
        history_size = 0
        if self.enabled and self.history_file.exists():
            try:
                history_size = self.history_file.stat().st_size
            except OSError:
                pass

        return {
            "enabled": self.enabled,
            "data_directory": str(self.data_dir),
            "history_file": str(self.history_file),
            "entries_stored": len(self._in_memory_history),
            "max_retention": self.max_entries,
            "file_size_bytes": history_size,
            "encryption": "None (Plain JSON on local machine)",
            "privacy_scope": "Local storage only; never transmitted to cloud services",
            "active_preferences": dict(self._in_memory_prefs),
        }
