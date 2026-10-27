#!/usr/bin/env python3
"""GhostShell - Phase 1 Entry Point.

A spooky, local-first AI developer assistant for the
"Ghost in the Machine" open-source AI challenge.

Usage:
    python main.py
    python main.py --no-animation
    python main.py --version
"""

from __future__ import annotations

import argparse
import sys

# Ensure UTF-8 standard stream handling on Windows
if sys.platform == "win32":
    for stream_name in ("stdout", "stderr", "stdin"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

from ghostshell import __version__
from ghostshell.commands import CommandAction, CommandHandler
from ghostshell.config import GhostConfig, get_default_config
from ghostshell.engine import PlaceholderEngine
from ghostshell.ui import GhostUI


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for GhostShell.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="GhostShell",
        description="A spooky, local-first AI developer assistant for the 'Ghost in the Machine' challenge.",
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Skip the CRT phosphor boot-up sequence.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"GhostShell v{__version__} (Phase 1)",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Print startup status diagnostics and exit.",
    )
    return parser.parse_args()


def run_repl(ui: GhostUI, handler: CommandHandler, engine: PlaceholderEngine) -> int:
    """Run the interactive GhostShell Read-Eval-Print Loop.

    Handles user inputs, slash commands, placeholder responses, Ctrl+C signals,
    and terminal edge cases with spooky flair. Guarantees that neither user
    input nor generated responses are ever executed as shell commands.

    Args:
        ui: Configured GhostUI renderer.
        handler: CommandHandler registry.
        engine: PlaceholderEngine instance.

    Returns:
        Process exit code (0 for clean termination).
    """
    # Enforce security invariant before entering REPL
    if ui.config.allow_command_execution:
        ui.render_error("FATAL: Security containment breached. Command execution must remain False.")
        return 1

    # Display initial startup sequence
    ui.render_startup_banner()

    while True:
        try:
            raw_input = ui.get_input()
        except KeyboardInterrupt:
            # Graceful handling of Ctrl+C
            ui.console.print("\n[bold #FFB000]👻 Spectral transmission interrupted (Ctrl+C).[/]")
            ui.render_goodbye()
            break
        except EOFError:
            # Graceful handling of EOF (Ctrl+D / Ctrl+Z)
            ui.console.print("\n[dim #2D7D46]Conduit closed via EOF signal.[/]")
            ui.render_goodbye()
            break

        stripped_input = raw_input.strip()

        # Ignore empty input lines
        if not stripped_input:
            continue

        # Check for built-in slash command
        if handler.is_command(stripped_input):
            result = handler.execute(stripped_input)

            if result.action == CommandAction.EXIT:
                ui.render_goodbye()
                break

            if result.action == CommandAction.CLEAR:
                ui.clear_screen()
                ui.render_startup_banner(animated=False)
                continue

            if result.action == CommandAction.ERROR:
                ui.render_error(result.message or "Unknown command error.")
                continue

            # CommandAction.CONTINUE with payload
            if result.data:
                payload_type = result.data.get("type")
                if payload_type == "help_all":
                    ui.render_help(result.data["docs"])
                elif payload_type == "help_single":
                    ui.render_single_help(result.data["doc"])
                elif payload_type == "status":
                    ui.render_status(result.data["info"])
                elif payload_type == "about":
                    ui.render_about(result.data["content"])
                else:
                    if result.message:
                        ui.console.print(result.message)
            elif result.message:
                ui.console.print(result.message)

            continue

        # Non-command input: Route to the Placeholder Response Engine
        # STRICT SECURITY: Input is NEVER executed. Treated only as text prompt.
        try:
            response = engine.process(stripped_input)
            ui.render_placeholder_response(response)
        except Exception as exc:
            ui.render_error(f"Spectral disturbance during conduit reflection: {exc}")

    return 0


def main() -> int:
    """Main execution function for GhostShell.

    Returns:
        Exit code integer.
    """
    args = parse_args()

    # Build configuration
    config = get_default_config()
    if args.no_animation:
        config.startup_animation = False

    ui = GhostUI(config=config)
    handler = CommandHandler()
    engine = PlaceholderEngine()

    if args.diagnostics:
        status_res = handler.execute("/status")
        if status_res.data and "info" in status_res.data:
            ui.render_status(status_res.data["info"])
        return 0

    return run_repl(ui=ui, handler=handler, engine=engine)


if __name__ == "__main__":
    sys.exit(main())
