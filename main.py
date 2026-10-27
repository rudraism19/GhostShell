#!/usr/bin/env python3
"""GhostShell - Phase 3 Entry Point.

A spooky, local-first AI developer assistant powered by local Gemma 3 1B
featuring the Possessed Java Debugger for the "Ghost in the Machine" open-source AI challenge.
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
from ghostshell.client import GemmaClient
from ghostshell.commands import CommandAction, CommandHandler
from ghostshell.config import GhostConfig, enable_windows_virtual_terminal, get_default_config, is_local_endpoint
from ghostshell.debugger import JavaDebugger, JavaDebugRequest
from ghostshell.engine import BaseEngine, GemmaEngine, PlaceholderEngine
from ghostshell.git_intel import GitIntelligence
from ghostshell.memory import GhostMemory
from ghostshell.persona import PersonaEngine
from ghostshell.ui import GhostUI


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for GhostShell.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="GhostShell",
        description="A spooky, local-first AI developer assistant & Possessed Java Debugger powered by local Gemma 3 1B.",
    )
    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Skip the CRT phosphor boot-up sequence.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"GhostShell v{__version__} (Phase 3-7 Master v1.0 - Possessed Java & Git Intelligence)",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Print startup status diagnostics and exit.",
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default=None,
        help="Custom URL for local OpenAI-compatible endpoint (default: http://127.0.0.1:9931/v1/chat/completions).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name expected by local llama.cpp server (default: gemma-3-1b-it).",
    )
    parser.add_argument(
        "--placeholder",
        action="store_true",
        help="Force Phase 1 standalone UI development placeholder mode.",
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable private local conversation memory persistence.",
    )
    parser.add_argument(
        "--persona",
        type=str,
        default=None,
        choices=["archivist", "poltergeist", "grim-debugger"],
        help="Set initial ghost personality archetype (default: grim-debugger).",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=None,
        choices=["green", "amber", "cyan", "monochrome"],
        help="Set initial phosphor color theme (default: green).",
    )
    return parser.parse_args()


def run_repl(
    ui: GhostUI,
    handler: CommandHandler,
    engine: BaseEngine,
    debugger: JavaDebugger | None = None,
) -> int:
    """Run the interactive GhostShell Read-Eval-Print Loop.

    Handles user inputs, slash commands, local Gemma responses, Java code
    debugging, Ctrl+C signals, and terminal edge cases with spooky flair.
    Guarantees that neither user input nor generated code is ever executed as shell commands.

    Args:
        ui: Configured GhostUI renderer.
        handler: CommandHandler registry.
        engine: Response engine (GemmaEngine or PlaceholderEngine).
        debugger: Optional JavaDebugger instance.

    Returns:
        Process exit code (0 for clean termination).
    """
    # Enforce security invariant before entering REPL
    if ui.config.allow_command_execution:
        ui.render_error("FATAL: Security containment breached. Command execution must remain False.")
        return 1

    client_instance = getattr(engine, "client", None)
    active_debugger = debugger or JavaDebugger(client=client_instance, config=ui.config)

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
        except (OSError, InterruptedError):
            # Absorb any transient interrupt caused by moving or resizing the window
            continue

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
                elif payload_type == "model_info":
                    ui.render_model_info(result.data["info"])
                elif payload_type == "about":
                    ui.render_about(result.data["content"])
                elif payload_type == "debug_interactive":
                    code = ui.prompt_multiline_input(
                        title="👻 POSSESSED JAVA DEBUGGER — SOURCE CODE",
                        instruction="Paste or type your Java code below.\nType ':done' on an empty line when finished, or ':cancel' to abort.",
                    )
                    if not code:
                        continue

                    err_msg = ui.prompt_multiline_input(
                        title="👻 POSSESSED JAVA DEBUGGER — COMPILER ERROR / LOGS (OPTIONAL)",
                        instruction="Paste compiler error, stack trace, or press ':done' if none. Type ':cancel' to skip.",
                    )
                    if err_msg is None:
                        err_msg = ""

                    req = JavaDebugRequest(code=code, error_message=err_msg)
                    with ui.status_spinner("👻 The possessed debugger is examining your Java bytecode..."):
                        debug_res = active_debugger.analyze(req)
                    ui.render_java_debug_result(debug_res)

                elif payload_type == "debug_inline":
                    inline_code = result.data.get("code", "")
                    req = JavaDebugRequest(code=inline_code)
                    with ui.status_spinner("👻 The possessed debugger is examining your Java bytecode..."):
                        debug_res = active_debugger.analyze(req)
                    ui.render_java_debug_result(debug_res)

                elif payload_type == "git_commits":
                    ui.render_git_commits(result.data["commits"])

                elif payload_type == "git_story":
                    ui.render_git_story(result.data["result"])

                elif payload_type == "git_review":
                    ui.render_git_review(result.data["result"])

                elif payload_type == "memory_history":
                    ui.render_memory_history(result.data["entries"])

                elif payload_type == "storage_diagnostics":
                    ui.render_storage_diagnostics(result.data["info"])

                elif payload_type == "persona_status":
                    ui.render_persona_status(result.data["current"], result.data["all"])

                elif payload_type == "theme_changed":
                    ui.render_theme_changed(result.data["theme"])

                else:
                    if result.message:
                        ui.console.print(result.message)
            elif result.message:
                ui.console.print(result.message)

            continue

        # Non-command input: Route to GemmaEngine or PlaceholderEngine
        # STRICT SECURITY: Input is NEVER executed. Treated only as text prompt.
        try:
            with ui.status_spinner("👻 The machine ghost is stirring... Inscribing spectral response..."):
                response = engine.process(stripped_input)

            if response.mode == "GEMMA_LOCAL":
                ui.render_gemma_response(response)
            elif response.mode in ("SERVER_OFFLINE", "SERVER_ERROR"):
                ui.render_model_offline(response)
            else:
                ui.render_placeholder_response(response)

        except Exception as exc:
            ui.render_error(f"Spectral disturbance during conduit reflection: {exc}")

    return 0


def main() -> int:
    """Main execution function for GhostShell.

    Returns:
        Exit code integer.
    """
    enable_windows_virtual_terminal()
    args = parse_args()

    # Build configuration
    config = get_default_config()
    if args.no_animation:
        config.startup_animation = False
    if args.endpoint:
        config.model_endpoint = args.endpoint
    if args.model:
        config.model_name = args.model
    if args.placeholder:
        config.force_placeholder = True
    if args.no_memory:
        config.memory_enabled = False
    if args.persona:
        config.active_persona = args.persona
    if args.theme:
        config.active_theme = args.theme

    # Setup subsystems
    memory = GhostMemory(
        data_dir=config.data_dir,
        enabled=config.memory_enabled,
    )
    persona_engine = PersonaEngine(
        default_persona=config.active_persona,
        default_theme=config.active_theme,
    )

    # Restore saved persona/theme preferences if available
    saved_persona = memory.get_preference("persona")
    if saved_persona and not args.persona:
        persona_engine.set_persona(saved_persona)

    saved_theme = memory.get_preference("theme")
    if saved_theme and not args.theme:
        persona_engine.set_theme(saved_theme)

    git_intel = GitIntelligence()

    # Setup client and engines
    client = GemmaClient(
        endpoint=config.model_endpoint,
        model_name=config.model_name,
        timeout=config.model_timeout,
    )

    if config.force_placeholder:
        engine: BaseEngine = PlaceholderEngine()
    else:
        engine = GemmaEngine(
            client=client,
            config=config,
            persona_engine=persona_engine,
            memory=memory,
        )

    debugger = JavaDebugger(client=client, config=config)
    ui = GhostUI(config=config)
    handler = CommandHandler(
        config=config,
        client=client,
        git_intel=git_intel,
        memory=memory,
        persona_engine=persona_engine,
    )

    # Warn if endpoint is not local
    if not is_local_endpoint(config.model_endpoint):
        ui.render_non_local_warning(config.model_endpoint)

    if args.diagnostics:
        status_res = handler.execute("/status")
        if status_res.data and "info" in status_res.data:
            ui.render_status(status_res.data["info"])
        return 0

    return run_repl(ui=ui, handler=handler, engine=engine, debugger=debugger)


if __name__ == "__main__":
    sys.exit(main())
