"""Command dispatcher and built-in slash commands for GhostShell.

Handles /help, /clear, /quit, /exit, /status, and /about.
Ensures no system or shell commands are ever executed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

from ghostshell.config import ALLOW_COMMAND_EXECUTION


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

    def __init__(self, start_time: float | None = None) -> None:
        """Initialize the command registry.

        Args:
            start_time: Monotonic timestamp when GhostShell was started.
        """
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
                description="Inspect the health of the spectral conduit and containment locks.",
                usage="/status",
                aliases=["/diag"],
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

        # Register aliases pointing to the same handler
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

        # Handle unknown slash command
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
        status_info = {
            "version": "0.1.0",
            "phase": "Phase 1 - Terminal UI & Control",
            "uptime_seconds": uptime_sec,
            "engine": "PlaceholderEngine (Standalone UI Mode)",
            "gemma_core": "Detached (Scheduled for Phase 2)",
            "command_execution": "STRICTLY FORBIDDEN (ALLOW_COMMAND_EXECUTION=False)",
            "security_sandbox": "ACTIVE",
            "platform": "Local-First / Windows PowerShell Ready",
        }
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "status", "info": status_info},
        )

    def _cmd_about(self, _args: list[str]) -> CommandResult:
        """Handle /about command."""
        about_text = (
            "[bold #00FF66]GhostShell[/bold #00FF66] is a spooky, local-first AI developer assistant "
            "engineered for the [bold #00F0FF]“Ghost in the Machine”[/bold #00F0FF] open-source AI challenge.\n\n"
            "• [bold #39FF14]The Premise:[/bold #39FF14] A haunted terminal companion that observes your command "
            "history, Git activity, and coding mistakes, translating them into eerie, intelligent commentary from "
            "a fictional ghost dwelling inside your machine.\n\n"
            "• [bold #39FF14]Local-First & Private:[/bold #39FF14] Designed to operate entirely on your hardware "
            "without leaking telemetry or relying on external cloud dependencies.\n\n"
            "• [bold #39FF14]Phase 1 Focus:[/bold #39FF14] Dark CRT phosphor terminal UI, graceful signal management, "
            "strict command containment, and modular response architecture ready for Google Gemma integration."
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "about", "content": about_text},
        )
