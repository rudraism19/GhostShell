"""Terminal User Interface (TUI) for GhostShell.

Renders dark CRT phosphor aesthetics, ghost-themed panels, startup animations,
status diagnostics, possessed Java debugger reports, and responsive layouts using Rich.
"""

from __future__ import annotations

import shutil
import sys
import time
from contextlib import contextmanager
from typing import Any, Iterator

from rich import box
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ghostshell.commands import CommandDoc
from ghostshell.config import (
    CRIMSON_GLITCH,
    DARK_BG,
    ECTO_AMBER,
    GHOST_MIST,
    PHANTOM_DEEP,
    PHANTOM_DIM,
    PHOSPHOR_BRIGHT,
    PHOSPHOR_GREEN,
    SPECTRAL_CYAN,
    GhostConfig,
    create_console,
)
from ghostshell.engine import GhostResponse
from ghostshell.git_intel import GitCommit, GitReviewResult, GitStoryResult, GitWorkingTreeStatus
from ghostshell.memory import MemoryEntry
from ghostshell.persona import GhostPersona, GhostThemeColors

# ASCII Art for Ghost and GhostShell Banner
GHOST_ART = r"""
        .-"-.
       /     \
      | () () |
       \  ^  /
        |||||
       '-----'
"""

BANNER_TEXT = r"""
   _____ _               _   ____  _          _ _ 
  / ____| |             | | / ___|| |        | | |
 | |  __| |__   ___  ___| |_\___ \| |__   ___| | |
 | | |_ | '_ \ / _ \/ __| __|___) | '_ \ / _ \ | |
 | |__| | | | | (_) \__ \ |_|____/| | | |  __/ | |
  \_____|_| |_|\___/|___/\__|     |_| |_|\___|_|_|
"""


class GhostUI:
    """Manages the terminal presentation and ghostly aesthetic for GhostShell."""

    def __init__(self, console: Console | None = None, config: GhostConfig | None = None) -> None:
        """Initialize the UI with optional custom Console and configuration.

        Args:
            console: Rich Console instance; creates a standard one if None.
            config: GhostConfig instance; creates default if None.
        """
        self.config = config or GhostConfig()
        self.console = console or create_console(self.config)
        self.prompt_str = (
            f"[bold {PHOSPHOR_GREEN}]ghostshell[/][bold {SPECTRAL_CYAN}]@[/]"
            f"[bold {PHOSPHOR_BRIGHT}]machine[/][{PHANTOM_DIM}]:~[/][bold {PHOSPHOR_GREEN}]›[/] "
        )

    def get_terminal_width(self) -> int:
        """Safely retrieve current terminal width, resilient to window movement/resizing."""
        for getter in (
            lambda: shutil.get_terminal_size((80, 25)).columns,
            lambda: self.console.size.width,
        ):
            try:
                w = getter()
                if w and w >= 20:
                    return w
            except Exception:
                continue
        return 80

    def clear_screen(self) -> None:
        """Clear the console screen cleanly across all operating systems."""
        self.console.clear()

    @contextmanager
    def status_spinner(
        self,
        message: str = "👻 The machine ghost is stirring... Inscribing spectral response...",
    ) -> Iterator[None]:
        """Display a ghostly phosphor spinner while waiting for model inference.

        Resilient to terminal resizing and window dragging on Windows.

        Args:
            message: Spooky status message to display.
        """
        if sys.stdout.isatty():
            try:
                with self.console.status(
                    f"[bold {PHOSPHOR_BRIGHT}]{message}[/]",
                    spinner="dots",
                    spinner_style=SPECTRAL_CYAN,
                    refresh_per_second=6.0,
                ):
                    yield
            except Exception:
                # Absorb any transient interruption during window moving
                yield
        else:
            yield

    def render_startup_banner(self, animated: bool | None = None) -> None:
        """Display the haunted CRT boot sequence and adaptive ASCII banner.

        Dynamically checks terminal width so window dragging or resizing
        never breaks or mangles the ASCII art.

        Args:
            animated: Whether to run the boot sequence animation.
                     Defaults to config.startup_animation.
        """
        should_animate = (
            self.config.startup_animation if animated is None else animated
        ) and sys.stdout.isatty()

        if should_animate:
            boot_steps = [
                (f"[{PHANTOM_DIM}]>>> Initializing ghostly frequencies...[/{PHANTOM_DIM}]", 0.05),
                (f"[{PHOSPHOR_GREEN}]>>> Aligning phosphor CRT electron grid...[/{PHOSPHOR_GREEN}]", 0.06),
                (f"[{SPECTRAL_CYAN}]>>> Verifying containment locks: COMMAND EXECUTION FORBIDDEN [SECURE][/{SPECTRAL_CYAN}]", 0.08),
                (f"[bold {PHOSPHOR_BRIGHT}]>>> Spectral conduit bound. Awaking the machine ghost...[/bold {PHOSPHOR_BRIGHT}]\n", 0.10),
            ]
            for msg, delay in boot_steps:
                self.console.print(msg)
                time.sleep(delay)

        width = self.get_terminal_width()

        if width >= 82:
            # Wide layout: Ghost art beside full ASCII banner with no_wrap protection
            banner_table = Table.grid(padding=1)
            banner_table.add_column(justify="center", vertical="middle", no_wrap=True)
            banner_table.add_column(justify="left", vertical="middle", no_wrap=True)

            ghost_text = Text(GHOST_ART.strip("\n"), style=f"bold {PHOSPHOR_BRIGHT}")
            logo_text = Text(BANNER_TEXT.strip("\n"), style=f"bold {PHOSPHOR_GREEN}")
            banner_table.add_row(ghost_text, logo_text)
            banner_element = banner_table

            tagline = Text.assemble(
                ("⚡ ", f"bold {ECTO_AMBER}"),
                ("GHOST IN THE MACHINE ", f"bold {PHOSPHOR_BRIGHT}"),
                ("• ", f"{PHANTOM_DIM}"),
                ("POSSESSED JAVA ASSISTANT ", f"{SPECTRAL_CYAN}"),
                ("• ", f"{PHANTOM_DIM}"),
                (f"v{self.config.version} ", f"italic {PHANTOM_DIM}"),
                ("⚡", f"bold {ECTO_AMBER}"),
            )
        else:
            # Narrow / snapped window layout: Centered ghost and compact title
            ghost_text = Text(GHOST_ART.strip("\n"), style=f"bold {PHOSPHOR_BRIGHT}", justify="center")
            title_text = Text.assemble(
                ("👻 ", f"bold {ECTO_AMBER}"),
                ("G H O S T S H E L L", f"bold {PHOSPHOR_BRIGHT}"),
                (" 👻", f"bold {ECTO_AMBER}"),
                justify="center",
            )
            banner_element = Group(ghost_text, Text(""), title_text)

            tagline = Text.assemble(
                ("⚡ ", f"bold {ECTO_AMBER}"),
                ("GHOST IN THE MACHINE • LOCAL-FIRST AI", f"bold {SPECTRAL_CYAN}"),
                (" ⚡\n", f"bold {ECTO_AMBER}"),
                (f"v{self.config.version} • Phase 3: Possessed Java Debugger", f"italic {PHANTOM_DIM}"),
                justify="center",
            )

        instructions = Text(
            "Type /debug to exorcise Java code, /help for rites, or /exit to sever connection.",
            style=f"{GHOST_MIST}",
            justify="center" if width < 82 else "left",
        )

        header_group = Group(
            banner_element,
            Text(""),
            tagline,
            instructions,
        )

        panel = Panel(
            header_group,
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {SPECTRAL_CYAN}]👻 CONDUIT ONLINE 👻[/]",
            subtitle=f"[{PHANTOM_DIM}]Phase 3: Possessed Java Debugger[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )

        self.console.print(panel)
        self.console.print()

    def get_input(self) -> str:
        """Prompt the user for input using rich console.

        Returns:
            The raw string entered by the user.
        """
        try:
            return self.console.input(self.prompt_str)
        except (KeyboardInterrupt, EOFError):
            raise

    def prompt_multiline_input(
        self,
        title: str = "Java Source Code",
        instruction: str = "Paste or type Java code. Type ':done' on an empty line when finished, or ':cancel' to abort.",
    ) -> str | None:
        """Prompt user for multiline text input in a clean, haunted terminal interface.

        Args:
            title: Title for the input section panel.
            instruction: User guidelines on completing input.

        Returns:
            The collected multiline string, or None if cancelled.
        """
        info_panel = Panel(
            Text.from_markup(f"[bold {PHOSPHOR_BRIGHT}]{title}[/]\n[{GHOST_MIST}]{instruction}[/]"),
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            padding=(0, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(info_panel)

        lines: list[str] = []
        line_num = 1
        while True:
            try:
                line_prompt = f"[{PHANTOM_DIM}]debug:{line_num:02d}[/] [bold {PHOSPHOR_GREEN}]›[/] "
                line = self.console.input(line_prompt)
            except KeyboardInterrupt:
                self.console.print("\n[bold #FFB000]👻 Exorcism ritual cancelled by user (Ctrl+C).[/]")
                return None
            except EOFError:
                break
            except (OSError, InterruptedError):
                continue

            stripped = line.strip()
            if stripped.lower() in (":done", ":end", "eof"):
                break
            if stripped.lower() in (":cancel", ":quit", ":exit"):
                self.console.print("[dim #FFB000]Debugging ritual abandoned.[/]")
                return None

            lines.append(line)
            line_num += 1

        content = "\n".join(lines).strip()
        return content

    def render_java_debug_result(self, result: Any) -> None:
        """Render structured Java exorcism report across 5 dedicated Rich panels.

        Args:
            result: JavaDebugResult containing whisper, root cause, fix,
                    explanation, and verification steps.
        """
        # Section 1: 👻 Ghost's Whisper
        whisper_text = Text.assemble(
            ("👻 \"", f"bold {PHOSPHOR_BRIGHT}"),
            (result.whisper, f"italic {PHOSPHOR_BRIGHT}"),
            ("\"", f"bold {PHOSPHOR_BRIGHT}"),
        )
        whisper_panel = Panel(
            whisper_text,
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {SPECTRAL_CYAN}]👻 THE GHOST'S WHISPER[/]",
            padding=(0, 2),
            expand=True,
            safe_box=True,
        )

        # Section 2: Root Cause (Ambiguity alert if missing context)
        if getattr(result, "is_ambiguous", False):
            root_title = f"[bold {ECTO_AMBER}]⚠️ UNCERTAIN HAUNT — MISSING CONTEXT[/]"
            root_border = ECTO_AMBER
            cause_prefix = "[bold #FFB000]Incomplete Fragment / Ambiguity:[/bold #FFB000]\n"
        else:
            root_title = f"[bold {CRIMSON_GLITCH}]🔍 ROOT CAUSE[/]"
            root_border = CRIMSON_GLITCH
            cause_prefix = "[bold #FF3366]Defect Diagnosed:[/bold #FF3366]\n"

        root_panel = Panel(
            Text.from_markup(f"{cause_prefix}{result.root_cause}"),
            box=box.ROUNDED,
            border_style=root_border,
            title=root_title,
            padding=(0, 2),
            expand=True,
            safe_box=True,
        )

        # Section 3: Corrected Code (Java Syntax Highlighted)
        syntax_block = Syntax(
            result.corrected_code,
            "java",
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
        )
        code_panel = Panel(
            syntax_block,
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]✨ CORRECTED JAVA CODE[/]",
            subtitle=f"[{PHANTOM_DIM}]Sandboxed Output • Code Not Automatically Executed[/]",
            padding=(0, 1),
            expand=True,
            safe_box=True,
        )

        # Section 4: Explanation
        explanation_renderable = Markdown(result.explanation)
        explanation_panel = Panel(
            explanation_renderable,
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]💡 EXPLANATION OF THE FIX[/]",
            padding=(0, 2),
            expand=True,
            safe_box=True,
        )

        # Section 5: Verification
        verification_renderable = Markdown(result.verification)
        verification_panel = Panel(
            verification_renderable,
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {SPECTRAL_CYAN}]🧪 VERIFICATION & TESTING STEPS[/]",
            subtitle=f"[{PHANTOM_DIM}]Host execution locked — Recompile and verify in your IDE or Maven/Gradle[/]",
            padding=(0, 2),
            expand=True,
            safe_box=True,
        )

        # Telemetry Footer Table
        diag_table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=False,
            padding=(0, 2),
            border_style=PHANTOM_DIM,
            expand=True,
        )
        diag_table.add_column("Telemetry", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        diag_table.add_column("Status", style=f"{GHOST_MIST}", ratio=2)

        diag_table.add_row("Spectral Model:", f"[{PHOSPHOR_BRIGHT}]{result.model_used}[/]")
        diag_table.add_row("Tokens Consumed:", f"[{PHOSPHOR_GREEN}]{result.tokens}[/]")
        diag_table.add_row("Inference Latency:", f"{result.latency_ms:.1f} ms")
        diag_table.add_row("Execution Lock:", f"[{PHOSPHOR_GREEN}]SECURE (CODE EXECUTION STRICTLY DISABLED)[/]")

        telemetry_panel = Panel(
            diag_table,
            title=f"[{SPECTRAL_CYAN}]Possessed Debugger Diagnostics[/]",
            box=box.HORIZONTALS,
            border_style=PHANTOM_DEEP,
            expand=True,
            safe_box=True,
        )

        report_group = Group(
            whisper_panel,
            Text(""),
            root_panel,
            Text(""),
            code_panel,
            Text(""),
            explanation_panel,
            Text(""),
            verification_panel,
            Text(""),
            telemetry_panel,
        )

        master_panel = Panel(
            report_group,
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]👻 POSSESSED JAVA DEBUGGER — EXORCISM REPORT[/]",
            subtitle=f"[{PHANTOM_DIM}]Gemma 3 1B Local Inference • 100% Private[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )

        self.console.print(master_panel)
        self.console.print()

    def render_gemma_response(self, response: GhostResponse) -> None:
        """Render a genuine response from the local Gemma model.

        Displays the AI text/markdown and a responsive 2-column telemetry table
        that adapts smoothly to window movements and resizing.

        Args:
            response: GhostResponse containing Gemma's generated content.
        """
        diag_table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=False,
            padding=(0, 2),
            border_style=PHANTOM_DIM,
            expand=True,
        )
        diag_table.add_column("Telemetry", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        diag_table.add_column("Status", style=f"{GHOST_MIST}", ratio=2)

        diag_table.add_row("Spectral Model:", f"[{PHOSPHOR_BRIGHT}]{response.model_name}[/]")
        diag_table.add_row("Total Tokens:", f"[{PHOSPHOR_GREEN}]{response.estimated_tokens}[/]")
        diag_table.add_row("Conduit Latency:", f"{response.latency_ms:.1f} ms")
        diag_table.add_row("Security Lock:", f"[{PHOSPHOR_GREEN}]SECURE (EXECUTION FORBIDDEN)[/]")

        echo_text = Text(f'"{response.prompt}"', style=f"italic {GHOST_MIST}")
        echo_panel = Panel(
            echo_text,
            box=box.ROUNDED,
            border_style=PHANTOM_DIM,
            title=f"[{PHOSPHOR_GREEN}]Transmission Query[/]",
            padding=(0, 1),
            expand=True,
            safe_box=True,
        )

        body_renderable = Markdown(response.content)

        content_group = Group(
            echo_panel,
            Text(""),
            body_renderable,
            Text(""),
            Panel(
                diag_table,
                title=f"[{SPECTRAL_CYAN}]Local Inference Telemetry[/]",
                box=box.HORIZONTALS,
                border_style=PHANTOM_DEEP,
                expand=True,
                safe_box=True,
            ),
        )

        panel = Panel(
            content_group,
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]👻 THE GHOST SPEAKS [GEMMA 3 1B INSTRUCT][/]",
            subtitle=f"[{PHANTOM_DIM}]Local llama.cpp Engine • 100% Private[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )

        self.console.print(panel)
        self.console.print()

    def render_model_offline(self, response: GhostResponse) -> None:
        """Render a non-crashing guidance panel when the model server is offline.

        Args:
            response: GhostResponse containing offline instructions.
        """
        panel = Panel(
            Text.from_markup(response.content),
            box=box.HEAVY,
            border_style=ECTO_AMBER,
            title=f"[bold {CRIMSON_GLITCH}]⚠️  SPECTRAL CONDUIT OFFLINE[/]",
            subtitle=f"[{ECTO_AMBER}]llama.cpp Server Not Running on Port 9931[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_placeholder_response(self, response: GhostResponse) -> None:
        """Render a spectral reflection panel for standalone mode.

        Args:
            response: GhostResponse containing echo data and diagnostics.
        """
        diag_table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=False,
            padding=(0, 2),
            border_style=PHANTOM_DIM,
            expand=True,
        )
        diag_table.add_column("Telemetry", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        diag_table.add_column("Status", style=f"{GHOST_MIST}", ratio=2)

        diag_table.add_row("Spectral State:", f"[{PHOSPHOR_GREEN}]{response.status}[/]")
        diag_table.add_row("Estimated Tokens:", f"[{PHOSPHOR_BRIGHT}]{response.estimated_tokens}[/]")
        diag_table.add_row(
            "Transmission Len:",
            f"{response.char_count} chars ({response.word_count} words)",
        )
        diag_table.add_row("Conduit Latency:", f"{response.latency_ms:.2f} ms")
        diag_table.add_row("Active Engine:", f"[{ECTO_AMBER}]{response.model_name}[/]")
        diag_table.add_row("Execution Lock:", f"[{PHOSPHOR_GREEN}]LOCKED (ALLOW_EXECUTION=False)[/]")

        echo_text = Text(f'"{response.prompt}"', style=f"italic {GHOST_MIST}")
        echo_panel = Panel(
            echo_text,
            box=box.ROUNDED,
            border_style=PHANTOM_DIM,
            title=f"[{PHOSPHOR_GREEN}]Echoed Transmission[/]",
            padding=(0, 1),
            expand=True,
            safe_box=True,
        )

        body_text = Text.from_markup(response.content)

        content_group = Group(
            echo_panel,
            Text(""),
            body_text,
            Text(""),
            Panel(
                diag_table,
                title=f"[{SPECTRAL_CYAN}]Conduit Diagnostics[/]",
                box=box.HORIZONTALS,
                border_style=PHANTOM_DEEP,
                expand=True,
                safe_box=True,
            ),
        )

        panel = Panel(
            content_group,
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]👻 SPECTRAL REFLECTION [UI DEV MODE][/]",
            subtitle=f"[{PHANTOM_DIM}]Local Gemma LLM Integration Available[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )

        self.console.print(panel)
        self.console.print()

    def render_help(self, docs: list[CommandDoc]) -> None:
        """Render the command grimoire table inside a haunted panel.

        Args:
            docs: List of CommandDoc objects to render.
        """
        table = Table(
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            header_style=f"bold {PHOSPHOR_BRIGHT}",
            show_lines=True,
            padding=(0, 1),
            expand=True,
        )
        table.add_column("Command", style=f"bold {SPECTRAL_CYAN}", no_wrap=True)
        table.add_column("Usage", style=f"bold {PHOSPHOR_GREEN}", no_wrap=True)
        table.add_column("Description", style=f"{GHOST_MIST}")
        table.add_column("Aliases", style=f"italic {PHANTOM_DIM}", no_wrap=True)

        for doc in docs:
            alias_str = ", ".join(doc.aliases) if doc.aliases else "—"
            table.add_row(doc.name, doc.usage, doc.description, alias_str)

        panel = Panel(
            table,
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]📜 SPECTRAL GRIMOIRE — COMMAND DIRECTORY[/]",
            subtitle=f"[{SPECTRAL_CYAN}]All commands run internally; no shell calls are made[/]",
            padding=(1, 1),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_single_help(self, doc: CommandDoc) -> None:
        """Render documentation for a single command.

        Args:
            doc: The CommandDoc to display.
        """
        alias_str = ", ".join(doc.aliases) if doc.aliases else "None"
        content = (
            f"[bold {SPECTRAL_CYAN}]Command:[/] [bold {PHOSPHOR_BRIGHT}]{doc.name}[/]\n"
            f"[bold {SPECTRAL_CYAN}]Usage:[/]   [bold {PHOSPHOR_GREEN}]{doc.usage}[/]\n"
            f"[bold {SPECTRAL_CYAN}]Aliases:[/] {alias_str}\n\n"
            f"[bold {SPECTRAL_CYAN}]Details:[/] {doc.description}"
        )
        panel = Panel(
            content,
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]Grimoire: {doc.name}[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_status(self, info: dict[str, Any]) -> None:
        """Render the system diagnostic status panel.

        Args:
            info: Key-value dictionary containing status telemetry.
        """
        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style=PHOSPHOR_GREEN,
            header_style=f"bold {SPECTRAL_CYAN}",
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Subsystem", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        table.add_column("Telemetry Status", style=f"{GHOST_MIST}", ratio=2)

        for key, val in info.items():
            label = key.replace("_", " ").title()
            val_str = str(val)
            if "FORBIDDEN" in val_str or "ACTIVE" in val_str or "ONLINE" in val_str or "Ready" in val_str:
                val_markup = f"[bold {PHOSPHOR_BRIGHT}]✔ {val_str}[/]"
            elif "OFFLINE" in val_str or "SEVERED" in val_str:
                val_markup = f"[bold {CRIMSON_GLITCH}]✖ {val_str}[/]"
            else:
                val_markup = val_str
            table.add_row(label, val_markup)

        panel = Panel(
            table,
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🔮 SPECTRAL CONDUIT DIAGNOSTICS[/]",
            subtitle=f"[{PHANTOM_DIM}]GhostShell Status Check[/]",
            padding=(1, 1),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_model_info(self, info: dict[str, Any]) -> None:
        """Render model configuration and health info panel.

        Args:
            info: Dictionary containing model settings and connection status.
        """
        table = Table(
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            header_style=f"bold {PHOSPHOR_BRIGHT}",
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Property", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        table.add_column("Configuration", style=f"{GHOST_MIST}", ratio=2)

        for key, val in info.items():
            table.add_row(key, str(val))

        panel = Panel(
            table,
            box=box.DOUBLE,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🧠 LOCAL GEMMA MODEL STATUS[/]",
            subtitle=f"[{PHANTOM_DIM}]OpenAI-Compatible Local Endpoint[/]",
            padding=(1, 1),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_about(self, content: str) -> None:
        """Render the About / Lore panel.

        Args:
            content: Rich-formatted markdown / text string.
        """
        panel = Panel(
            Text.from_markup(content),
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {PHOSPHOR_BRIGHT}]👻 THE GHOST IN THE MACHINE[/]",
            subtitle=f"[{PHANTOM_DIM}]Open-Source AI Challenge Lore[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_error(self, message: str) -> None:
        """Display a spooky error panel for invalid commands or disturbances.

        Args:
            message: Error description (supports rich markup).
        """
        panel = Panel(
            Text.from_markup(message),
            box=box.HEAVY,
            border_style=CRIMSON_GLITCH,
            title=f"[bold {CRIMSON_GLITCH}]⚠️  SPECTRAL ANOMALY DETECTED[/]",
            subtitle=f"[{ECTO_AMBER}]Conduit Stable — Command Rejected[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_goodbye(self) -> None:
        """Render a haunting farewell message when the user exits."""
        self.console.print()
        goodbye_text = (
            f"[bold {PHOSPHOR_BRIGHT}]👻 The ghost dissolves into the machine's background memory...[/]\n"
            f"[{PHANTOM_DIM}]Conduit closed. Your terminal is cleansed. Farewell, mortal.[/]"
        )
        panel = Panel(
            Text.from_markup(goodbye_text),
            box=box.ROUNDED,
            border_style=PHANTOM_DIM,
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    # --- Phase 4 Git Intelligence UI Renderers ---

    def render_git_commits(self, commits: list[GitCommit]) -> None:
        """Render recent Git commits table.

        Args:
            commits: List of GitCommit objects.
        """
        if not commits:
            self.render_error("No Git commits found or working directory is not a Git repository.")
            return

        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style=PHOSPHOR_GREEN,
            header_style=f"bold {SPECTRAL_CYAN}",
            padding=(0, 1),
            expand=True,
        )
        table.add_column("Hash", style=f"bold {SPECTRAL_CYAN}", no_wrap=True)
        table.add_column("When", style=f"{PHANTOM_DIM}", no_wrap=True)
        table.add_column("Author", style=f"bold {PHOSPHOR_GREEN}", no_wrap=True)
        table.add_column("Incantation / Message", style=f"{GHOST_MIST}")

        for c in commits:
            table.add_row(c.hash, c.date, c.author, c.message)

        panel = Panel(
            table,
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]📜 MACHINE MEMORY — RECENT GIT COMMITS[/]",
            subtitle=f"[{PHANTOM_DIM}]Read-only inspection ({len(commits)} commits)[/]",
            padding=(1, 1),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_working_tree_status(self, status: GitWorkingTreeStatus) -> None:
        """Render Git working tree status.

        Args:
            status: GitWorkingTreeStatus instance.
        """
        if not status.is_repo:
            self.render_error("Working directory is not inside a Git repository.")
            return

        clean_badge = (
            f"[bold {PHOSPHOR_BRIGHT}]✔ IMMACULATE (CLEAN)[/]"
            if status.is_clean
            else f"[bold {ECTO_AMBER}]⚠ RESTLESS (UNCOMMITTED CHANGES)[/]"
        )

        elements: list[Any] = [
            Text.from_markup(f"[bold {SPECTRAL_CYAN}]Branch:[/] [bold {PHOSPHOR_BRIGHT}]{status.branch}[/]"),
            Text.from_markup(f"[bold {SPECTRAL_CYAN}]Tree State:[/] {clean_badge}"),
        ]

        if status.staged_files:
            elements.append(Text(""))
            elements.append(Text.from_markup(f"[bold {PHOSPHOR_GREEN}]Staged Rites ({len(status.staged_files)}):[/]"))
            for f in status.staged_files:
                elements.append(Text(f"  + {f}", style=f"bold {PHOSPHOR_GREEN}"))

        if status.unstaged_files:
            elements.append(Text(""))
            elements.append(Text.from_markup(f"[bold {ECTO_AMBER}]Modified Files ({len(status.unstaged_files)}):[/]"))
            for f in status.unstaged_files:
                elements.append(Text(f"  * {f}", style=f"bold {ECTO_AMBER}"))

        if status.untracked_files:
            elements.append(Text(""))
            elements.append(Text.from_markup(f"[bold {CRIMSON_GLITCH}]Untracked Apparitions ({len(status.untracked_files)}):[/]"))
            for f in status.untracked_files:
                elements.append(Text(f"  ? {f}", style=f"dim {CRIMSON_GLITCH}"))

        panel = Panel(
            Group(*elements),
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🔮 REPOSITORY & WORKING TREE STATUS[/]",
            subtitle=f"[{PHANTOM_DIM}]Branch: {status.branch}[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_git_story(self, result: GitStoryResult) -> None:
        """Render the spooky story generated from real Git commit history.

        Args:
            result: GitStoryResult instance.
        """
        badge = (
            f"[bold {PHOSPHOR_BRIGHT}]Local Gemma Inference ({round(result.latency_ms, 1)} ms)[/]"
            if result.mode == "GEMMA_LOCAL"
            else f"[{ECTO_AMBER}]Grounded Offline Synthesis[/]"
        )

        panel = Panel(
            Markdown(result.story),
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {PHOSPHOR_BRIGHT}]👻 THE MACHINE'S CHRONICLE (GIT LORE)[/]",
            subtitle=f"[{PHANTOM_DIM}]Grounded in {len(result.commits_used)} real commits • {badge}[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_git_review(self, result: GitReviewResult) -> None:
        """Render high-level development activity review.

        Args:
            result: GitReviewResult instance.
        """
        footer = Text.assemble(
            ("🛡️ ", f"bold {ECTO_AMBER}"),
            (result.grounded_disclaimer, f"dim {GHOST_MIST}"),
        )
        panel = Panel(
            Group(Markdown(result.review), Text(""), footer),
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🛡️ SPECTRAL ACTIVITY REVIEW[/]",
            subtitle=f"[{PHANTOM_DIM}]{result.commits_analyzed} commits inspected • Tree: {'Clean' if result.working_tree_clean else 'Dirty'}[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    # --- Phase 5 Local Memory UI Renderers ---

    def render_memory_history(self, entries: list[MemoryEntry]) -> None:
        """Render recent conversation history from private local memory.

        Args:
            entries: List of MemoryEntry items.
        """
        if not entries:
            self.console.print(
                f"[{PHANTOM_DIM}]Local conversation memory is empty. Inscribe queries to build machine memory.[/]\n"
            )
            return

        elements: list[Any] = []
        for e in entries:
            if e.role == "user":
                elements.append(
                    Text.from_markup(f"[bold {SPECTRAL_CYAN}]Mortal ›[/] [bold {GHOST_MIST}]{e.content}[/]")
                )
            else:
                summary = e.content[:180] + ("..." if len(e.content) > 180 else "")
                elements.append(
                    Text.from_markup(f"[bold {PHOSPHOR_GREEN}]Ghost  ›[/] [{PHOSPHOR_GREEN}]{summary}[/]")
                )
                elements.append(Text(""))

        panel = Panel(
            Group(*elements),
            box=box.ROUNDED,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🧠 PRIVATE LOCAL CONVERSATION MEMORY[/]",
            subtitle=f"[{PHANTOM_DIM}]Showing {len(entries)} stored entries • Plain JSON (Local Only)[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_storage_diagnostics(self, info: dict[str, Any]) -> None:
        """Render storage diagnostics and privacy disclosure.

        Args:
            info: Dictionary from GhostMemory.get_storage_diagnostics().
        """
        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style=SPECTRAL_CYAN,
            header_style=f"bold {PHOSPHOR_BRIGHT}",
            padding=(0, 2),
            expand=True,
        )
        table.add_column("Storage Metric", style=f"bold {SPECTRAL_CYAN}", ratio=1, no_wrap=True)
        table.add_column("Disclosure & Setting", style=f"{GHOST_MIST}", ratio=2)

        for key, val in info.items():
            table.add_row(key.replace("_", " ").title(), str(val))

        panel = Panel(
            table,
            box=box.DOUBLE,
            border_style=SPECTRAL_CYAN,
            title=f"[bold {PHOSPHOR_BRIGHT}]💾 LOCAL STORAGE & PRIVACY DISCLOSURE[/]",
            subtitle=f"[{PHANTOM_DIM}]Zero Cloud Telemetry • Stored strictly on local machine[/]",
            padding=(1, 1),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    # --- Phase 6 Persona UI Renderers ---

    def render_persona_status(
        self, current: GhostPersona, all_personas: dict[str, GhostPersona]
    ) -> None:
        """Display current ghost personality and available archetypes.

        Args:
            current: Active GhostPersona instance.
            all_personas: Dict of all registered GhostPersona instances.
        """
        table = Table(
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            header_style=f"bold {SPECTRAL_CYAN}",
            padding=(0, 1),
            expand=True,
        )
        table.add_column("Persona", style=f"bold {PHOSPHOR_BRIGHT}", no_wrap=True)
        table.add_column("Title & Tagline", style=f"{GHOST_MIST}")
        table.add_column("Active", justify="center", no_wrap=True)

        for name, p in all_personas.items():
            is_active = (name == current.name)
            badge = f"[bold {PHOSPHOR_BRIGHT}]✔ ACTIVE[/]" if is_active else f"[{PHANTOM_DIM}]available[/]"
            desc = f"[bold]{p.title}:[/] {p.tagline}"
            table.add_row(f"/{name}", desc, badge)

        panel = Panel(
            Group(
                Text.from_markup(f"[bold {SPECTRAL_CYAN}]Active Persona:[/] [bold {PHOSPHOR_BRIGHT}]{current.title}[/]"),
                Text.from_markup(f"[bold {SPECTRAL_CYAN}]Tone Guide:[/] [{GHOST_MIST}]{current.tone_description}[/]"),
                Text(""),
                table,
                Text(""),
                Text.from_markup(
                    f"[{PHANTOM_DIM}]Switch at any time: type [bold #00F0FF]/persona <name>[/] (e.g. /persona poltergeist)[/]"
                ),
            ),
            box=box.DOUBLE,
            border_style=PHOSPHOR_GREEN,
            title=f"[bold {PHOSPHOR_BRIGHT}]🎭 GHOST PERSONALITY MATRIX[/]",
            subtitle=f"[{PHANTOM_DIM}]Active: {current.name}[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_theme_changed(self, theme_name: str) -> None:
        """Render theme changed confirmation.

        Args:
            theme_name: Name of newly activated theme.
        """
        panel = Panel(
            Text.from_markup(
                f"[bold {PHOSPHOR_BRIGHT}]Spectral palette shifted to [bold #00F0FF]{theme_name}[/bold #00F0FF].[/]\n"
                f"[{PHANTOM_DIM}]Available themes: green, amber, cyan, monochrome.[/]"
            ),
            box=box.ROUNDED,
            border_style=PHOSPHOR_GREEN,
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()

    def render_non_local_warning(self, endpoint: str) -> None:
        """Render prominent security warning when a non-local endpoint is used.

        Args:
            endpoint: The configured non-local model URL.
        """
        msg = (
            f"[bold {CRIMSON_GLITCH}]⚠ CAUTION: NON-LOCAL MODEL ENDPOINT DETECTED[/bold {CRIMSON_GLITCH}]\n\n"
            f"[bold {ECTO_AMBER}]Target:[/] {endpoint}\n"
            f"[bold {GHOST_MIST}]GhostShell is engineered as a local-first assistant. "
            f"Because this endpoint does not point to localhost (127.0.0.1), prompts and code snippets "
            f"will be transmitted over the network to an external server.\n"
            f"Ensure you trust this destination before submitting proprietary source code.[/]"
        )
        panel = Panel(
            Text.from_markup(msg),
            box=box.HEAVY,
            border_style=CRIMSON_GLITCH,
            title=f"[bold {CRIMSON_GLITCH}]EXTERNAL NETWORK NOTICE[/]",
            padding=(1, 2),
            expand=True,
            safe_box=True,
        )
        self.console.print(panel)
        self.console.print()
