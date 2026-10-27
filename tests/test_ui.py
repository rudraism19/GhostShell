"""Unit tests for GhostShell Terminal User Interface (GhostUI)."""

from __future__ import annotations

from unittest.mock import patch
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
    """Verify banner rendering contains GhostShell, tagline, and Phase 3."""
    ui.render_startup_banner(animated=False)
    output = mock_console.export_text()
    assert "GHOST IN THE MACHINE" in output
    assert "CONDUIT ONLINE" in output
    assert "Phase 3" in output


def test_render_gemma_response(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of genuine Gemma response with Markdown and telemetry."""
    response = GhostResponse(
        prompt="Explain recursion",
        content="Recursion occurs when a function calls itself.\n\n```python\ndef fact(n):\n    return 1 if n <= 1 else n * fact(n - 1)\n```",
        mode="GEMMA_LOCAL",
        status="ONLINE_BOUND",
        model_name="Gemma 3 1B (gemma-3-1b-it)",
        char_count=17,
        word_count=2,
        estimated_tokens=42,
        latency_ms=150.0,
    )
    ui.render_gemma_response(response)
    output = mock_console.export_text()
    assert "THE GHOST SPEAKS" in output
    assert "GEMMA 3 1B INSTRUCT" in output
    assert "Explain recursion" in output
    assert "Recursion occurs" in output
    assert "def fact(n):" in output
    assert "Total Tokens:" in output
    assert "150.0 ms" in output


def test_render_model_offline(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of non-crashing offline guidance panel."""
    response = GhostResponse(
        prompt="Explain memory leak",
        content="Spectral Conduit Severed: Start llama-server on port 9931.",
        mode="SERVER_OFFLINE",
        status="CONDUIT_SEVERED",
    )
    ui.render_model_offline(response)
    output = mock_console.export_text()
    assert "SPECTRAL CONDUIT OFFLINE" in output
    assert "llama.cpp Server Not Running on Port 9931" in output
    assert "Start llama-server on port 9931" in output


def test_render_model_info(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of /model inspection panel."""
    info = {
        "Model Name": "gemma-3-1b-it",
        "Local Endpoint": "http://127.0.0.1:8080/v1/chat/completions",
        "Server Status": "ONLINE",
    }
    ui.render_model_info(info)
    output = mock_console.export_text()
    assert "LOCAL GEMMA MODEL STATUS" in output
    assert "gemma-3-1b-it" in output


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


def test_render_help_all(ui: GhostUI, mock_console: Console) -> None:
    """Verify grimoire table rendering."""
    docs = [
        CommandDoc(name="/help", description="Help command", usage="/help", aliases=["/?"]),
        CommandDoc(name="/model", description="Model info", usage="/model", aliases=["/gemma"]),
    ]
    ui.render_help(docs)
    output = mock_console.export_text()
    assert "SPECTRAL GRIMOIRE" in output
    assert "/help" in output
    assert "/model" in output


def test_status_spinner_context_manager(ui: GhostUI) -> None:
    """Ensure status_spinner runs without error."""
    with ui.status_spinner("Testing spinner"):
        pass


def test_render_java_debug_result(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of 5 sections in Java exorcism report."""
    from ghostshell.debugger import JavaDebugResult
    res = JavaDebugResult(
        whisper="A silent specter in the bytecode.",
        root_cause="Null pointer dereference on line 5.",
        corrected_code="String s = \"ghost\";\nSystem.out.println(s.length());",
        explanation="Initialize string prior to method call.",
        verification="Compile and run in terminal.",
        latency_ms=75.0,
        tokens=88,
    )
    ui.render_java_debug_result(res)
    output = mock_console.export_text()
    assert "THE GHOST'S WHISPER" in output
    assert "A silent specter" in output
    assert "ROOT CAUSE" in output
    assert "CORRECTED JAVA CODE" in output
    assert "EXPLANATION OF THE FIX" in output
    assert "VERIFICATION" in output
    assert "75.0 ms" in output


def test_prompt_multiline_input_done(ui: GhostUI) -> None:
    """Verify multiline input stops on :done."""
    with patch.object(ui.console, "input", side_effect=["for (int i = 0; i < 5; i++) {", "    System.out.println(i);", "}", ":done"]):
        text = ui.prompt_multiline_input("Code", "Type :done")
    assert text is not None
    assert "System.out.println(i);" in text


def test_prompt_multiline_input_cancel(ui: GhostUI) -> None:
    """Verify multiline input aborts on :cancel."""
    with patch.object(ui.console, "input", side_effect=["class Broken {", ":cancel"]):
        text = ui.prompt_multiline_input("Code", "Type :done")
    assert text is None


def test_render_git_commits(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of Git commit table."""
    from ghostshell.git_intel import GitCommit
    commits = [
        GitCommit(hash="a17108a", author="GhostDev", date="1 hour ago", message="Fix broken loop"),
    ]
    ui.render_git_commits(commits)
    output = mock_console.export_text()
    assert "RECENT GIT COMMITS" in output
    assert "a17108a" in output
    assert "GhostDev" in output
    assert "Fix broken loop" in output


def test_render_working_tree_status(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of Git working tree status."""
    from ghostshell.git_intel import GitWorkingTreeStatus
    status = GitWorkingTreeStatus(
        is_repo=True,
        branch="main",
        staged_files=["file1.py"],
        unstaged_files=["file2.py"],
        untracked_files=["new.py"],
        is_clean=False,
    )
    ui.render_working_tree_status(status)
    output = mock_console.export_text()
    assert "REPOSITORY & WORKING TREE STATUS" in output
    assert "main" in output
    assert "RESTLESS" in output
    assert "file1.py" in output


def test_render_memory_history(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of conversation history turns."""
    from ghostshell.memory import MemoryEntry
    entries = [
        MemoryEntry(timestamp=100.0, role="user", content="Hello machine ghost"),
        MemoryEntry(timestamp=101.0, role="assistant", content="Greetings mortal"),
    ]
    ui.render_memory_history(entries)
    output = mock_console.export_text()
    assert "PRIVATE LOCAL CONVERSATION MEMORY" in output
    assert "Hello machine ghost" in output
    assert "Greetings mortal" in output


def test_render_persona_status(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of persona status panel."""
    from ghostshell.persona import AVAILABLE_PERSONAS
    current = AVAILABLE_PERSONAS["grim-debugger"]
    ui.render_persona_status(current, AVAILABLE_PERSONAS)
    output = mock_console.export_text()
    assert "GHOST PERSONALITY MATRIX" in output
    assert "Grim Debugger" in output
    assert "ACTIVE" in output


def test_render_non_local_warning(ui: GhostUI, mock_console: Console) -> None:
    """Verify rendering of prominent non-local endpoint alert."""
    ui.render_non_local_warning("https://api.openai.com/v1")
    output = mock_console.export_text()
    assert "NON-LOCAL MODEL ENDPOINT DETECTED" in output
    assert "https://api.openai.com/v1" in output
