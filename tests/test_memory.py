"""Unit tests for GhostShell private local memory store (Phase 5)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from ghostshell.memory import GhostMemory, MemoryEntry


@pytest.fixture
def memory_dir(tmp_path: Path) -> Path:
    """Fixture providing an isolated temporary directory for memory storage."""
    return tmp_path / "ghost_store"


def test_memory_record_and_read(memory_dir: Path) -> None:
    """Verify recording conversation turns and reading them back."""
    memory = GhostMemory(data_dir=memory_dir, enabled=True, max_entries=10)

    memory.record_turn(
        user_prompt="Who haunts this silicon?",
        assistant_response="I am the ghost in your machine.",
        metadata={"tokens": 15},
    )

    history = memory.get_history()
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Who haunts this silicon?"
    assert history[1].role == "assistant"
    assert history[1].content == "I am the ghost in your machine."
    assert history[1].metadata["tokens"] == 15


def test_memory_persistence_on_disk(memory_dir: Path) -> None:
    """Verify memory persists across distinct GhostMemory instances."""
    mem1 = GhostMemory(data_dir=memory_dir, enabled=True)
    mem1.record_turn("Turn 1", "Reply 1")

    # Re-instantiate pointing to the same folder
    mem2 = GhostMemory(data_dir=memory_dir, enabled=True)
    history = mem2.get_history()

    assert len(history) == 2
    assert history[0].content == "Turn 1"
    assert history[1].content == "Reply 1"


def test_memory_fifo_truncation(memory_dir: Path) -> None:
    """Verify old entries are truncated when max_entries bound is reached."""
    max_entries = 4  # Holds 2 turns (4 entries)
    memory = GhostMemory(data_dir=memory_dir, enabled=True, max_entries=max_entries)

    memory.record_turn("Prompt 1", "Resp 1")
    memory.record_turn("Prompt 2", "Resp 2")
    memory.record_turn("Prompt 3", "Resp 3")

    history = memory.get_history()
    assert len(history) == 4
    # Oldest turn (Prompt 1) should have been evicted
    assert history[0].content == "Prompt 2"
    assert history[1].content == "Resp 2"
    assert history[2].content == "Prompt 3"
    assert history[3].content == "Resp 3"


def test_memory_corrupt_file_recovery(memory_dir: Path) -> None:
    """Verify corruption recovery: invalid JSON is quarantined without crashing."""
    memory_dir.mkdir(parents=True, exist_ok=True)
    bad_file = memory_dir / "history.json"
    bad_file.write_text("{ corrupt json data ::: [ ]", encoding="utf-8")

    # Loading should catch JSONDecodeError, rename to .bak, and start cleanly
    mem = GhostMemory(data_dir=memory_dir, enabled=True)
    assert mem.get_history() == []

    # Ensure quarantine backup exists
    bak_file = memory_dir / "history.json.corrupt.bak"
    assert bak_file.exists()


def test_memory_disabled_mode(memory_dir: Path) -> None:
    """Verify zero file persistence when memory is disabled."""
    mem = GhostMemory(data_dir=memory_dir, enabled=False)

    mem.record_turn("Ghost query", "Ghost reply")
    # Works in memory buffer
    assert len(mem.get_history()) == 2

    # But no disk files are created
    assert not (memory_dir / "history.json").exists()


def test_memory_clear_and_forget(memory_dir: Path) -> None:
    """Verify clear() clears history file and forget() purges all files."""
    mem = GhostMemory(data_dir=memory_dir, enabled=True)
    mem.record_turn("Query", "Reply")
    mem.set_preference("persona", "archivist")

    assert (memory_dir / "history.json").exists()
    assert (memory_dir / "preferences.json").exists()

    # Clear only wipes history
    mem.clear()
    assert len(mem.get_history()) == 0
    assert not (memory_dir / "history.json").exists()
    assert (memory_dir / "preferences.json").exists()

    # Forget wipes preferences too
    res = mem.forget()
    assert res is True
    assert not (memory_dir / "preferences.json").exists()


def test_memory_preferences(memory_dir: Path) -> None:
    """Verify preference saving and loading across instances."""
    mem1 = GhostMemory(data_dir=memory_dir, enabled=True)
    mem1.set_preference("theme", "amber")
    mem1.set_preference("persona", "poltergeist")

    mem2 = GhostMemory(data_dir=memory_dir, enabled=True)
    assert mem2.get_preference("theme") == "amber"
    assert mem2.get_preference("persona") == "poltergeist"
    assert mem2.get_preference("nonexistent", default="default_val") == "default_val"


def test_memory_context_messages_for_prompt(memory_dir: Path) -> None:
    """Verify format of bounded context pairs passed to Gemma."""
    mem = GhostMemory(data_dir=memory_dir, enabled=True)
    mem.record_turn("Turn 1 prompt", "Turn 1 answer")
    mem.record_turn("Turn 2 prompt", "Turn 2 answer")

    context = mem.get_context_messages(max_pairs=1)
    # 1 pair = 2 messages (the most recent)
    assert len(context) == 2
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Turn 2 prompt"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Turn 2 answer"


def test_memory_storage_diagnostics(memory_dir: Path) -> None:
    """Verify diagnostic disclosure accurately states plain JSON and zero cloud."""
    mem = GhostMemory(data_dir=memory_dir, enabled=True)
    diag = mem.get_storage_diagnostics()

    assert diag["enabled"] is True
    assert "Plain JSON" in diag["encryption"]
    assert "never transmitted to cloud" in diag["privacy_scope"].lower()
    assert str(memory_dir) in diag["data_directory"]
