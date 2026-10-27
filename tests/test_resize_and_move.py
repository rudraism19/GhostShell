"""Tests verifying UI rendering resilience across dynamic terminal widths and window movements."""

from __future__ import annotations

import pytest
from rich.console import Console

from ghostshell.commands import CommandDoc
from ghostshell.config import GhostConfig, enable_windows_virtual_terminal
from ghostshell.engine import GhostResponse
from ghostshell.ui import GhostUI


@pytest.mark.parametrize("width", [50, 65, 75, 80, 95, 120])
def test_startup_banner_across_widths(width: int) -> None:
    """Ensure startup banner renders cleanly without crashing across narrow and wide terminal sizes."""
    console = Console(record=True, width=width, legacy_windows=False)
    ui = GhostUI(console=console, config=GhostConfig(startup_animation=False))
    ui.render_startup_banner(animated=False)

    output = console.export_text()
    assert "CONDUIT ONLINE" in output
    assert "GHOST IN THE MACHINE" in output


@pytest.mark.parametrize("width", [55, 70, 80, 100])
def test_gemma_response_across_widths(width: int) -> None:
    """Ensure Gemma response and telemetry table scale without ellipses or crushed lines."""
    console = Console(record=True, width=width, legacy_windows=False)
    ui = GhostUI(console=console)

    response = GhostResponse(
        prompt="Explain quicksort",
        content="Quicksort divides and conquers using a pivot element.",
        mode="GEMMA_LOCAL",
        model_name="Gemma 3 1B (gemma-3-1b-it)",
        estimated_tokens=45,
        latency_ms=88.5,
    )
    ui.render_gemma_response(response)

    output = console.export_text()
    assert "THE GHOST SPEAKS" in output
    assert "Quicksort" in output
    assert "Gemma 3 1B" in output
    assert "gemma-3-1b-it" in output
    assert "88.5 ms" in output


@pytest.mark.parametrize("width", [55, 70, 80, 100])
def test_help_table_across_widths(width: int) -> None:
    """Ensure help table adapts cleanly when moving or resizing the window."""
    console = Console(record=True, width=width, legacy_windows=False)
    ui = GhostUI(console=console)
    docs = [
        CommandDoc(name="/help", description="Show grimoire rites", usage="/help", aliases=["/?"]),
        CommandDoc(name="/model", description="Inspect local model", usage="/model", aliases=["/gemma"]),
    ]
    ui.render_help(docs)

    output = console.export_text()
    assert "SPECTRAL GRIMOIRE" in output
    assert "/help" in output
    assert "/model" in output


def test_enable_windows_virtual_terminal_safe_call() -> None:
    """Verify enable_windows_virtual_terminal does not raise exceptions."""
    enable_windows_virtual_terminal()
