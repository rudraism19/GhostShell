"""Command dispatcher and built-in slash commands for GhostShell.

Handles /help, /clear, /quit, /exit, /status, /about, and /model.
Ensures no system or shell commands are ever executed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

from ghostshell.client import GemmaClient
from ghostshell.config import ALLOW_COMMAND_EXECUTION, GhostConfig


class CommandAction(str, Enum):
    """Actions resulting from executing a built-in slash command."""

    CONTINUE = "continue"
    CLEAR = "clear"
    EXIT = "exit"
    ERROR = "error"


@dataclass
class CommandResult:
    """Outcome of a dispatched command.

    Attributes:
        action: The CommandAction directive for the REPL loop.
        message: Optional user-facing message or explanation.
        data: Optional payload for rendering rich UI components.
    """

    action: CommandAction
    message: str | None = None
    data: dict[str, Any] | None = None


@dataclass
class CommandDoc:
    """Documentation metadata for a slash command."""

    name: str
    description: str
    usage: str
    aliases: list[str]


class CommandHandler:
    """Registry and dispatcher for GhostShell slash commands.

    Strictly handles internal assistant commands. Never forwards commands
    to PowerShell, CMD, bash, or OS subprocesses.
    """

    def __init__(
        self,
        config: GhostConfig | None = None,
        client: GemmaClient | None = None,
        start_time: float | None = None,
    ) -> None:
        """Initialize the command registry.

        Args:
            config: Optional GhostConfig instance.
            client: Optional GemmaClient instance for health checks.
            start_time: Monotonic timestamp when GhostShell was started.
        """
        self.config = config or GhostConfig()
        self.client = client
        self.start_time = start_time if start_time is not None else time.monotonic()
        self._commands: dict[str, Callable[[list[str]], CommandResult]] = {}
        self._docs: dict[str, CommandDoc] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register the built-in slash commands."""
        # /help
        self.register(
            name="help",
            handler=self._cmd_help,
            doc=CommandDoc(
                name="/help",
                description="Summon the grimoire of available commands and usage guidelines.",
                usage="/help [command]",
                aliases=["/?"],
            ),
        )

        # /clear
        self.register(
            name="clear",
            handler=self._cmd_clear,
            doc=CommandDoc(
                name="/clear",
                description="Banish previous screen spirits and refresh the spectral viewport.",
                usage="/clear",
                aliases=["/cls"],
            ),
        )

        # /exit & /quit
        exit_doc = CommandDoc(
            name="/exit",
            description="Release the ghost and return safely to the host operating system.",
            usage="/exit or /quit",
            aliases=["/quit", "/q"],
        )
        self.register(name="exit", handler=self._cmd_exit, doc=exit_doc)
        self.register(name="quit", handler=self._cmd_exit, doc=exit_doc)

        # /status
        self.register(
            name="status",
            handler=self._cmd_status,
            doc=CommandDoc(
                name="/status",
                description="Inspect the health of the spectral conduit, model server, and locks.",
                usage="/status",
                aliases=["/diag"],
            ),
        )

        # /model
        self.register(
            name="model",
            handler=self._cmd_model,
            doc=CommandDoc(
                name="/model",
                description="Inspect the local Gemma model endpoint, name, and connection status.",
                usage="/model",
                aliases=["/gemma"],
            ),
        )

        # /about
        self.register(
            name="about",
            handler=self._cmd_about,
            doc=CommandDoc(
                name="/about",
                description="Learn the lore and purpose behind the Ghost in the Machine.",
                usage="/about",
                aliases=[],
            ),
        )

    def register(
        self,
        name: str,
        handler: Callable[[list[str]], CommandResult],
        doc: CommandDoc,
    ) -> None:
        """Register a new slash command.

        Args:
            name: The command identifier (without leading slash).
            handler: Callable taking argument list and returning CommandResult.
            doc: Command documentation.
        """
        key = name.lower().lstrip("/")
        self._commands[key] = handler
        self._docs[key] = doc

        for alias in doc.aliases:
            alias_key = alias.lower().lstrip("/")
            self._commands[alias_key] = handler

    @staticmethod
    def is_command(text: str) -> bool:
        """Check if an input string is a slash command."""
        return text.strip().startswith("/")

    def get_registered_docs(self) -> list[CommandDoc]:
        """Return a deduplicated list of command documentation objects."""
        seen: set[str] = set()
        docs: list[CommandDoc] = []
        for doc in self._docs.values():
            if doc.name not in seen:
                seen.add(doc.name)
                docs.append(doc)
        return docs

    def execute(self, text: str) -> CommandResult:
        """Parse and execute a slash command string.

        Guaranteed never to invoke system commands or subshells.

        Args:
            text: Raw command string starting with '/'.

        Returns:
            CommandResult specifying action and UI payload.
        """
        stripped = text.strip()
        if not stripped.startswith("/"):
            return CommandResult(
                action=CommandAction.ERROR,
                message="Not a slash command. Transmissions should begin with '/' or be plain text prompts.",
            )

        parts = stripped[1:].split()
        if not parts:
            return CommandResult(
                action=CommandAction.ERROR,
                message="Empty command invocation. Type [bold #00F0FF]/help[/] for a list of available commands.",
            )

        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name in self._commands:
            try:
                return self._commands[cmd_name](args)
            except Exception as exc:
                return CommandResult(
                    action=CommandAction.ERROR,
                    message=f"Spectral aberration executing /{cmd_name}: {exc}",
                )

        available = ", ".join(f"/{name}" for name in sorted(self._docs.keys()))
        return CommandResult(
            action=CommandAction.ERROR,
            message=(
                f"Unknown ritual [bold #FF3366]/{cmd_name}[/].\n"
                f"The ghost knows only: {available}.\n"
                f"Type [bold #00F0FF]/help[/] to view invocation rites."
            ),
        )

    # --- Built-in Command Implementations ---

    def _cmd_help(self, args: list[str]) -> CommandResult:
        """Handle /help command."""
        if args:
            sub = args[0].lower().lstrip("/")
            if sub in self._docs:
                doc = self._docs[sub]
                return CommandResult(
                    action=CommandAction.CONTINUE,
                    data={"type": "help_single", "doc": doc},
                )
            return CommandResult(
                action=CommandAction.ERROR,
                message=f"No grimoire entry found for [bold #FF3366]/{sub}[/]. Type /help for all commands.",
            )

        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "help_all", "docs": self.get_registered_docs()},
        )

    def _cmd_clear(self, _args: list[str]) -> CommandResult:
        """Handle /clear command."""
        return CommandResult(
            action=CommandAction.CLEAR,
            message="Terminal cleared. Spectral conduit cleansed.",
        )

    def _cmd_exit(self, _args: list[str]) -> CommandResult:
        """Handle /exit or /quit command."""
        return CommandResult(
            action=CommandAction.EXIT,
            message="Ghost released. Severing the spectral link...",
        )

    def _cmd_status(self, _args: list[str]) -> CommandResult:
        """Handle /status command."""
        uptime_sec = round(time.monotonic() - self.start_time, 1)

        # Check local model server health
        server_status = "NOT CONFIGURED"
        if self.client:
            is_online = self.client.check_health(timeout=1.0)
            server_status = (
                f"ONLINE (Receptive at {self.client.endpoint})"
                if is_online
                else f"OFFLINE (llama-server not detected on port 8080)"
            )

        status_info = {
            "version": self.config.version,
            "phase": "Phase 2 - Local Gemma 3 1B Integration",
            "uptime_seconds": uptime_sec,
            "model_server": server_status,
            "model_name": self.config.model_name,
            "command_execution": "STRICTLY FORBIDDEN (ALLOW_COMMAND_EXECUTION=False)",
            "security_sandbox": "ACTIVE",
            "inference_mode": "100% Local-First / Zero Cloud Telemetry",
            "platform": "Windows PowerShell & Terminal Ready",
        }
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "status", "info": status_info},
        )

    def _cmd_model(self, _args: list[str]) -> CommandResult:
        """Handle /model command to display local model configuration."""
        is_online = self.client.check_health(timeout=1.0) if self.client else False
        info = {
            "Model Name": self.config.model_name,
            "Local Endpoint": self.config.model_endpoint,
            "Server Status": "ONLINE (Ready for queries)" if is_online else "OFFLINE (llama-server not running)",
            "Quantization Target": "Gemma 3 1B Instruct GGUF (e.g. Q4_K_M)",
            "Target Hardware": "8 GB RAM Windows Laptop (CPU Inference)",
            "Cloud Dependencies": "NONE (100% Local Inference)",
            "Request Timeout": f"{self.config.model_timeout}s",
        }
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "model_info", "info": info},
        )

    def _cmd_about(self, _args: list[str]) -> CommandResult:
        """Handle /about command."""
        about_text = (
            "[bold #00FF66]GhostShell[/bold #00FF66] is a spooky, local-first AI developer assistant "
            "engineered for the [bold #00F0FF]“Ghost in the Machine”[/bold #00F0FF] open-source AI challenge.\n\n"
            "• [bold #39FF14]The Premise:[/bold #39FF14] A haunted terminal companion that observes your command "
            "history, Git activity, and coding mistakes, translating them into eerie, intelligent commentary from "
            "a fictional ghost dwelling inside your machine.\n\n"
            "• [bold #39FF14]Local-First & Private:[/bold #39FF14] Powered by [bold #00F0FF]Gemma 3 1B Instruct[/bold #00F0FF] "
            "running locally via [bold #00F0FF]llama.cpp server[/bold #00F0FF]. No cloud APIs, no subscriptions, "
            "and zero telemetry.\n\n"
            "• [bold #39FF14]Sandboxed Safety:[/bold #39FF14] GhostShell operates strictly as an advisory assistant. "
            "It never executes commands supplied by users or generated by Gemma."
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "about", "content": about_text},
        )
