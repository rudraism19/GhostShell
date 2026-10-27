"""Command dispatcher and built-in slash commands for GhostShell.

Handles /help, /debug, /clear, /quit, /exit, /status, /model, /about,
/git, /story, /review, /githelp, /history, /forget, /storage, /persona, and /theme.
Ensures no system or shell commands are ever executed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

from ghostshell.client import GemmaClient
from ghostshell.config import ALLOW_COMMAND_EXECUTION, GhostConfig
from ghostshell.git_intel import GitIntelligence
from ghostshell.memory import GhostMemory
from ghostshell.persona import AVAILABLE_PERSONAS, AVAILABLE_THEMES, PersonaEngine


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
        git_intel: GitIntelligence | None = None,
        memory: GhostMemory | None = None,
        persona_engine: PersonaEngine | None = None,
    ) -> None:
        """Initialize the command registry.

        Args:
            config: Optional GhostConfig instance.
            client: Optional GemmaClient instance for health checks.
            start_time: Monotonic timestamp when GhostShell was started.
            git_intel: Optional GitIntelligence service.
            memory: Optional GhostMemory store.
            persona_engine: Optional PersonaEngine instance.
        """
        self.config = config or GhostConfig()
        self.client = client
        self.start_time = start_time if start_time is not None else time.monotonic()
        self.git_intel = git_intel or GitIntelligence()
        self.memory = memory
        self.persona_engine = persona_engine or PersonaEngine(
            default_persona=self.config.active_persona,
            default_theme=self.config.active_theme,
        )

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

        # /debug
        self.register(
            name="debug",
            handler=self._cmd_debug,
            doc=CommandDoc(
                name="/debug",
                description="Invoke the Possessed Java Debugger to diagnose compiler errors and loop bugs.",
                usage="/debug [code]",
                aliases=["/javadebug"],
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
                description="Inspect the health of the spectral conduit, model server, Git repository, and locks.",
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

        # --- Phase 4 Git Intelligence Rites ---

        # /git
        self.register(
            name="git",
            handler=self._cmd_git,
            doc=CommandDoc(
                name="/git",
                description="Summarize the five most recent commits in the machine's Git memory.",
                usage="/git [count]",
                aliases=["/commits", "/log"],
            ),
        )

        # /story
        self.register(
            name="story",
            handler=self._cmd_story,
            doc=CommandDoc(
                name="/story",
                description="Generate an eerie gothic tale grounded strictly in real recent commit history.",
                usage="/story [count]",
                aliases=["/gitstory"],
            ),
        )

        # /review
        self.register(
            name="review",
            handler=self._cmd_review,
            doc=CommandDoc(
                name="/review",
                description="Provide a cautious high-level review of recent development activity.",
                usage="/review [count]",
                aliases=["/gitreview"],
            ),
        )

        # /githelp
        self.register(
            name="githelp",
            handler=self._cmd_githelp,
            doc=CommandDoc(
                name="/githelp",
                description="Display quick guide for all repository intelligence rites.",
                usage="/githelp",
                aliases=[],
            ),
        )

        # --- Phase 5 Private Local Memory Rites ---

        # /history
        self.register(
            name="history",
            handler=self._cmd_history,
            doc=CommandDoc(
                name="/history",
                description="Inspect recent conversation turns preserved in private local memory.",
                usage="/history [limit]",
                aliases=["/hist"],
            ),
        )

        # /forget
        self.register(
            name="forget",
            handler=self._cmd_forget,
            doc=CommandDoc(
                name="/forget",
                description="Purge all persistent conversation history and local preference files.",
                usage="/forget",
                aliases=["/purge"],
            ),
        )

        # /storage
        self.register(
            name="storage",
            handler=self._cmd_storage,
            doc=CommandDoc(
                name="/storage",
                description="Inspect local data storage path, file sizes, and privacy disclosure.",
                usage="/storage",
                aliases=["/privacy"],
            ),
        )

        # --- Phase 6 Persona & Theme Rites ---

        # /persona
        self.register(
            name="persona",
            handler=self._cmd_persona,
            doc=CommandDoc(
                name="/persona",
                description="Inspect or shift the active ghost archetype (archivist, poltergeist, grim-debugger).",
                usage="/persona [name]",
                aliases=["/personality"],
            ),
        )

        # /theme
        self.register(
            name="theme",
            handler=self._cmd_theme,
            doc=CommandDoc(
                name="/theme",
                description="Inspect or shift the terminal phosphor theme (green, amber, cyan, monochrome).",
                usage="/theme [name]",
                aliases=["/colors"],
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

    def _cmd_debug(self, args: list[str]) -> CommandResult:
        """Handle /debug command for Java code exorcisms."""
        if args:
            return CommandResult(
                action=CommandAction.CONTINUE,
                data={"type": "debug_inline", "code": " ".join(args)},
            )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "debug_interactive"},
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

        server_status = "NOT CONFIGURED"
        if self.client:
            is_online = self.client.check_health(timeout=1.0)
            server_status = (
                f"ONLINE (Receptive at {self.client.endpoint})"
                if is_online
                else f"OFFLINE (llama-server not detected on port 9931)"
            )

        status_info: dict[str, Any] = {
            "version": self.config.version,
            "phase": "Master v1.0 - Possessed Java & Git Intelligence",
            "uptime_seconds": uptime_sec,
            "model_server": server_status,
            "model_name": self.config.model_name,
            "command_execution": "STRICTLY FORBIDDEN (ALLOW_COMMAND_EXECUTION=False)",
            "security_sandbox": "ACTIVE",
            "debugger_module": "ghostshell.debugger (Java Exorcisms Active)",
            "git_intelligence": "ghostshell.git_intel (Safe Read-Only Subprocess)",
            "local_memory": f"ghostshell.memory ({'ENABLED' if (self.memory and self.memory.enabled) else 'DISABLED'})",
            "active_persona": self.persona_engine.current_persona.title,
            "active_theme": self.persona_engine.current_theme.name,
            "inference_mode": "100% Local-First / Zero Cloud Telemetry",
            "platform": "Windows PowerShell & Terminal Ready",
        }

        if self.git_intel.is_inside_work_tree():
            tree = self.git_intel.get_working_tree_status()
            status_info["git_branch"] = tree.branch
            status_info["working_tree"] = (
                "Clean (Immaculate)"
                if tree.is_clean
                else f"Dirty ({len(tree.staged_files)} staged, {len(tree.unstaged_files)} modified, {len(tree.untracked_files)} untracked)"
            )

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
            "Max Debug Tokens": f"{self.config.debug_max_tokens}",
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
            "• [bold #39FF14]Possessed Java Debugger:[/bold #39FF14] Diagnoses compiler errors, loop variable bugs "
            "(such as incrementing the outer loop variable), type mismatches, and null pointers using local "
            "[bold #00F0FF]Gemma 3 1B[/bold #00F0FF].\n\n"
            "• [bold #39FF14]Machine Memory & Git Intelligence:[/bold #39FF14] Read-only commit inspection, "
            "grounded gothic narratives, and cautious development reviews.\n\n"
            "• [bold #39FF14]Private Local Memory:[/bold #39FF14] Zero cloud telemetry. Conversation turns and preferences "
            "are stored in plain JSON on your local computer and can be purged at will with /forget.\n\n"
            "• [bold #39FF14]Sandboxed Safety:[/bold #39FF14] GhostShell operates strictly as an advisory assistant. "
            "It never executes commands or code supplied by users or generated by Gemma."
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "about", "content": about_text},
        )

    # --- Phase 4 Git Intelligence Handlers ---

    def _cmd_git(self, args: list[str]) -> CommandResult:
        """Handle /git command to list recent commits."""
        limit = 5
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                limit = 5

        commits = self.git_intel.get_recent_commits(limit=limit)
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "git_commits", "commits": commits},
        )

    def _cmd_story(self, args: list[str]) -> CommandResult:
        """Handle /story command to summon a commit-grounded ghost tale."""
        limit = 5
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                limit = 5

        sys_prompt = self.persona_engine.build_system_prompt(self.config.model_system_prompt)
        story_res = self.git_intel.generate_story(
            client=self.client,
            system_prompt=sys_prompt,
            limit=limit,
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "git_story", "result": story_res},
        )

    def _cmd_review(self, args: list[str]) -> CommandResult:
        """Handle /review command for cautious activity feedback."""
        limit = 5
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                limit = 5

        sys_prompt = self.persona_engine.build_system_prompt(self.config.model_system_prompt)
        review_res = self.git_intel.generate_review(
            client=self.client,
            system_prompt=sys_prompt,
            limit=limit,
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "git_review", "result": review_res},
        )

    def _cmd_githelp(self, _args: list[str]) -> CommandResult:
        """Handle /githelp command."""
        msg = (
            "[bold #00FF66]GhostShell Git Intelligence Rites:[/bold #00FF66]\n\n"
            "• [bold #00F0FF]/git [count][/bold #00F0FF]      - Inspect the 5 most recent commit records.\n"
            "• [bold #00F0FF]/status[/bold #00F0FF]           - Inspect branch and working-tree cleanliness.\n"
            "• [bold #00F0FF]/story [count][/bold #00F0FF]    - Weave a gothic narrative grounded in actual commit logs.\n"
            "• [bold #00F0FF]/review [count][/bold #00F0FF]   - Cautious high-level development velocity review.\n\n"
            "[dim]All Git operations are strictly read-only subprocess calls. "
            "GhostShell will never stage, commit, push, or alter your repository.[/dim]"
        )
        return CommandResult(
            action=CommandAction.CONTINUE,
            message=msg,
        )

    # --- Phase 5 Private Memory Handlers ---

    def _cmd_history(self, args: list[str]) -> CommandResult:
        """Handle /history command."""
        limit = None
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                limit = None

        if self.memory:
            entries = self.memory.get_history(limit=limit)
        else:
            entries = []

        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "memory_history", "entries": entries},
        )

    def _cmd_forget(self, _args: list[str]) -> CommandResult:
        """Handle /forget command to purge persistent memory."""
        if self.memory:
            success = self.memory.forget()
            msg = (
                "[bold #39FF14]✔ Ghost memory purged.[/bold #39FF14] "
                "All conversation traces and local preference files have been banished from disk."
                if success
                else "[bold #FFB000]Memory purged in session; file deletion could not be verified.[/bold #FFB000]"
            )
        else:
            msg = "[dim]Memory store is not active in this session.[/dim]"

        return CommandResult(
            action=CommandAction.CONTINUE,
            message=msg,
        )

    def _cmd_storage(self, _args: list[str]) -> CommandResult:
        """Handle /storage command to inspect local data diagnostics."""
        if self.memory:
            info = self.memory.get_storage_diagnostics()
        else:
            info = {"enabled": False, "status": "Memory subsystem detached."}

        return CommandResult(
            action=CommandAction.CONTINUE,
            data={"type": "storage_diagnostics", "info": info},
        )

    # --- Phase 6 Persona & Theme Handlers ---

    def _cmd_persona(self, args: list[str]) -> CommandResult:
        """Handle /persona command to inspect or switch archetypes."""
        if not args:
            return CommandResult(
                action=CommandAction.CONTINUE,
                data={
                    "type": "persona_status",
                    "current": self.persona_engine.current_persona,
                    "all": AVAILABLE_PERSONAS,
                },
            )

        target = args[0].strip().lower()
        if self.persona_engine.set_persona(target):
            active = self.persona_engine.current_persona
            if self.memory and self.memory.enabled:
                self.memory.set_preference("persona", active.name)
            return CommandResult(
                action=CommandAction.CONTINUE,
                message=(
                    f"👻 Ghostly frequency shifted to [bold #00F0FF]{active.title}[/bold #00F0FF].\n"
                    f"[{active.tagline}]"
                ),
            )

        valid = ", ".join(f"'{k}'" for k in AVAILABLE_PERSONAS.keys())
        return CommandResult(
            action=CommandAction.ERROR,
            message=(
                f"Unknown archetype [bold #FF3366]'{target}'[/].\n"
                f"Available personas: {valid}.\n"
                f"Usage: [bold #00F0FF]/persona <name>[/]"
            ),
        )

    def _cmd_theme(self, args: list[str]) -> CommandResult:
        """Handle /theme command to inspect or switch color palettes."""
        if not args:
            current_name = self.persona_engine.current_theme.name
            themes_list = ", ".join(
                f"[bold #00FF66]{k}[/]" if k == current_name else k
                for k in AVAILABLE_THEMES.keys()
            )
            return CommandResult(
                action=CommandAction.CONTINUE,
                message=(
                    f"Active theme: [bold #00FF66]{current_name}[/].\n"
                    f"Available themes: {themes_list}.\n"
                    f"Type [bold #00F0FF]/theme <name>[/] to shift palette."
                ),
            )

        target = args[0].strip().lower()
        if self.persona_engine.set_theme(target):
            if self.memory and self.memory.enabled:
                self.memory.set_preference("theme", self.persona_engine.current_theme.name)
            return CommandResult(
                action=CommandAction.CONTINUE,
                data={"type": "theme_changed", "theme": self.persona_engine.current_theme.name},
            )

        valid = ", ".join(AVAILABLE_THEMES.keys())
        return CommandResult(
            action=CommandAction.ERROR,
            message=f"Unknown theme '{target}'. Available themes: {valid}.",
        )
