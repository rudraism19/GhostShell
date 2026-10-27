"""Unit tests for GhostShell REPL loop and signal handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from ghostshell.commands import CommandAction, CommandHandler, CommandResult
from ghostshell.config import GhostConfig
from ghostshell.engine import PlaceholderEngine
from ghostshell.ui import GhostUI
from main import run_repl


@pytest.fixture
def repl_env() -> tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]:
    """Fixture providing components for testing the REPL loop."""
    console = Console(record=True, width=100)
    config = GhostConfig(startup_animation=False)
    ui = GhostUI(console=console, config=config)
    handler = CommandHandler()
    engine = PlaceholderEngine()
    return ui, handler, engine, console


def test_repl_exit_command(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test that /exit command terminates the loop gracefully."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=["/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "CONDUIT ONLINE" in output
    assert "Farewell, mortal." in output


def test_repl_keyboard_interrupt(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test that Ctrl+C (KeyboardInterrupt) exits gracefully without crash."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=KeyboardInterrupt):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "interrupted (Ctrl+C)" in output
    assert "Farewell, mortal." in output


def test_repl_eof_error(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test that EOFError (Ctrl+D / Ctrl+Z) exits gracefully."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=EOFError):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "Conduit closed via EOF signal" in output
    assert "Farewell, mortal." in output


def test_repl_empty_input_skips(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test that blank lines are skipped until /exit."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=["", "   ", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0


def test_repl_clear_command(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test /clear invokes clear_screen and re-displays banner."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=["/clear", "/exit"]):
        with patch.object(ui, "clear_screen") as mock_clear:
            exit_code = run_repl(ui, handler, engine)
            assert mock_clear.called

    assert exit_code == 0


def test_repl_unknown_command_shows_error(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test invalid command triggers error panel without breaking REPL."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=["/not_a_valid_command", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "SPECTRAL ANOMALY DETECTED" in output
    assert "Unknown ritual" in output


def test_repl_plain_text_routes_to_engine(repl_env: tuple[GhostUI, CommandHandler, PlaceholderEngine, Console]) -> None:
    """Test conversational text prompt routes to placeholder response engine."""
    ui, handler, engine, console = repl_env

    with patch.object(ui, "get_input", side_effect=["What is an echo?", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "SPECTRAL REFLECTION" in output
    assert "What is an echo?" in output


def test_repl_security_guard_on_allow_execution() -> None:
    """Test that if security flag was somehow True, run_repl aborts with code 1."""
    console = Console(record=True)
    config = GhostConfig()
    # Bypass property setter directly in test to test safety guard
    object.__setattr__(config, "allow_command_execution", True)

    ui = GhostUI(console=console, config=config)
    handler = CommandHandler()
    engine = PlaceholderEngine()

    exit_code = run_repl(ui, handler, engine)
    assert exit_code == 1
