"""Unit tests for GhostShell REPL loop, Gemma responses, and signal handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.commands import CommandAction, CommandHandler
from ghostshell.config import GhostConfig
from ghostshell.engine import GemmaEngine, PlaceholderEngine
from ghostshell.ui import GhostUI
from main import run_repl


@pytest.fixture
def repl_env() -> tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]:
    """Fixture providing components for testing the REPL loop with GemmaEngine."""
    console = Console(record=True, width=100)
    config = GhostConfig(startup_animation=False)
    ui = GhostUI(console=console, config=config)
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
    mock_client.model_name = "gemma-3-1b-it"
    mock_client.check_health.return_value = True

    handler = CommandHandler(config=config, client=mock_client)
    engine = GemmaEngine(client=mock_client, config=config)
    return ui, handler, engine, console, mock_client


def test_repl_gemma_successful_query(
    repl_env: tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]
) -> None:
    """Test standard query receives and renders genuine Gemma response."""
    ui, handler, engine, console, mock_client = repl_env

    mock_client.chat_completion.return_value = CompletionResponse(
        content="Always close file descriptors to prevent ghost leaks.",
        model="gemma-3-1b-it",
        prompt_tokens=15,
        completion_tokens=10,
        total_tokens=25,
        latency_ms=90.0,
    )

    with patch.object(ui, "get_input", side_effect=["How to handle files?", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "THE GHOST SPEAKS" in output
    assert "Always close file descriptors" in output
    assert "Farewell, mortal." in output


def test_repl_gemma_server_offline_non_crashing(
    repl_env: tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]
) -> None:
    """Requirement 6: When server is stopped, GhostShell displays useful error and remains usable."""
    ui, handler, engine, console, mock_client = repl_env

    mock_client.chat_completion.side_effect = ModelServerError(
        message="Connection refused",
        is_offline=True,
        endpoint="http://127.0.0.1:8080/v1/chat/completions",
    )

    with patch.object(ui, "get_input", side_effect=["Analyze this function", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "SPECTRAL CONDUIT OFFLINE" in output
    assert "llama-server.exe" in output
    assert "Farewell, mortal." in output


def test_repl_slash_model_command(
    repl_env: tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]
) -> None:
    """Test /model slash command displays model properties in REPL."""
    ui, handler, engine, console, _ = repl_env

    with patch.object(ui, "get_input", side_effect=["/model", "/exit"]):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "LOCAL GEMMA MODEL STATUS" in output
    assert "gemma-3-1b-it" in output


def test_repl_keyboard_interrupt(
    repl_env: tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]
) -> None:
    """Test that Ctrl+C (KeyboardInterrupt) exits gracefully."""
    ui, handler, engine, console, _ = repl_env

    with patch.object(ui, "get_input", side_effect=KeyboardInterrupt):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "interrupted (Ctrl+C)" in output
    assert "Farewell, mortal." in output


def test_repl_eof_error(
    repl_env: tuple[GhostUI, CommandHandler, GemmaEngine, Console, MagicMock]
) -> None:
    """Test that EOFError exits gracefully."""
    ui, handler, engine, console, _ = repl_env

    with patch.object(ui, "get_input", side_effect=EOFError):
        exit_code = run_repl(ui, handler, engine)

    assert exit_code == 0
    output = console.export_text()
    assert "Conduit closed via EOF signal" in output
    assert "Farewell, mortal." in output
