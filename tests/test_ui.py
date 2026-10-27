"""Unit tests for GhostShell Terminal User Interface (GhostUI)."""

from __future__ import annotations

import pytest
from rich.console import Console

from ghostshell.commands import CommandDoc
from ghostshell.config import GhostConfig
from ghostshell.engine import GhostResponse
from ghostshell.ui import GhostUI


@pytest.fixture
def mock_console() -> Console:
    """Fixture providing an in-memory Console that records output."""
    return Console(record=True, width=100)


@pytest.fixture
def ui(mock_console: Console) -> GhostUI:
    """Fixture providing a GhostUI instance backed by a recording console."""
    config = GhostConfig(startup_animation=False)
    return GhostUI(console=mock_console, config=config)


def test_render_startup_banner(ui: GhostUI, mock_console: Console) -> None:
    """Verify banner rendering contains GhostShell and tagline."""
    ui.render_startup_banner(animated=False)
    output = mock_console.export_text()
    assert "GHOST IN THE MACHINE" in output
    assert "CONDUIT ONLINE" in output
    assert "Phase 1" in output


def test_render_placeholder_response(ui: GhostUI, mock_console: Console) -> None:
    """Verify placeholder response panel renders echo and diagnostic table."""
    response = GhostResponse(
        prompt="ghost echo test",
        content="UI Development Mode Active: Testing conduit.",
        char_count=15,
        word_count=3,
        estimated_tokens=4,
        latency_ms=0.15,
    )
    ui.render_placeholder_response(response)
    output = mock_console.export_text()
    assert "SPECTRAL REFLECTION" in output
    assert "ghost echo test" in output
    assert "Conduit Diagnostics" in output
    assert "Est. Tokens:" in output
    assert "UI Development Mode Active" in output


def test_render_help_all(ui: GhostUI, mock_console: Console) -> None:
    """Verify grimoire table rendering."""
    docs = [
        CommandDoc(name="/help", description="Help command", usage="/help", aliases=["/?"]),
        CommandDoc(name="/exit", description="Exit command", usage="/exit", aliases=["/quit"]),
    ]
    ui.render_help(docs)
    output = mock_console.export_text()
    assert "SPECTRAL GRIMOIRE" in output
    assert "/help" in output
    assert "/exit" in output


def test_render_single_help(ui: GhostUI, mock_console: Console) -> None:
    """Verify single command help rendering."""
    doc = CommandDoc(name="/clear", description="Clear screen", usage="/clear", aliases=["/cls"])
    ui.render_single_help(doc)
    output = mock_console.export_text()
    assert "Grimoire: /clear" in output
    assert "Usage:" in output
    assert "/cls" in output


def test_render_status(ui: GhostUI, mock_console: Console) -> None:
    """Verify status diagnostics panel rendering."""
    info = {
        "version": "0.1.0",
        "phase": "Phase 1 - Terminal UI & Control",
        "engine": "PlaceholderEngine",
        "command_execution": "STRICTLY FORBIDDEN",
    }
    ui.render_status(info)
    output = mock_console.export_text()
    assert "SPECTRAL CONDUIT DIAGNOSTICS" in output
    assert "PlaceholderEngine" in output
    assert "FORBIDDEN" in output


def test_render_about(ui: GhostUI, mock_console: Console) -> None:
    """Verify about panel rendering."""
    ui.render_about("[bold]Haunted assistant[/bold]")
    output = mock_console.export_text()
    assert "THE GHOST IN THE MACHINE" in output
    assert "Haunted assistant" in output


def test_render_error(ui: GhostUI, mock_console: Console) -> None:
    """Verify error panel rendering."""
    ui.render_error("Severe spectral rupture detected!")
    output = mock_console.export_text()
    assert "SPECTRAL ANOMALY DETECTED" in output
    assert "Severe spectral rupture detected!" in output


def test_render_goodbye(ui: GhostUI, mock_console: Console) -> None:
    """Verify farewell message rendering."""
    ui.render_goodbye()
    output = mock_console.export_text()
    assert "The ghost dissolves into the machine" in output
    assert "Farewell, mortal." in output


def test_terminal_width_resilience(ui: GhostUI) -> None:
    """Ensure get_terminal_width returns at least 40 and does not crash."""
    width = ui.get_terminal_width()
    assert width >= 40
