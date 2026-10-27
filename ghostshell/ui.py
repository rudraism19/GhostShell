"""Terminal User Interface (TUI) for GhostShell.

Renders dark CRT phosphor aesthetics, ghost-themed panels, startup animations,
status diagnostics, and responsive layouts using the Rich library.
Engineered to be completely stable and resilient when moving or resizing the terminal window.
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
                ("LOCAL-FIRST AI COMPANION ", f"{SPECTRAL_CYAN}"),
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
                (f"v{self.config.version} • Phase 2: Local Gemma 3 1B", f"italic {PHANTOM_DIM}"),
                justify="center",
            )

        instructions = Text(
            "Type /help for grimoire rites or /exit to sever connection.",
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
            subtitle=f"[{PHANTOM_DIM}]Phase 2: Local Gemma 3 1B Integration[/]",
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

    def render_gemma_response(self, response: GhostResponse) -> None:
        """Render a genuine response from the local Gemma model.

        Displays the AI text/markdown and a responsive 2-column telemetry table
        that adapts smoothly to window movements and resizing.

        Args:
            response: GhostResponse containing Gemma's generated content.
        """
        # Responsive 2-column Telemetry Table (no cramped 4-column overflow)
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

        # Transmission Echo Panel
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

        # Render Markdown body from Gemma
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
            subtitle=f"[{ECTO_AMBER}]llama.cpp Server Not Running on Port 8080[/]",
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
