"""Unit tests for GhostShell response engines and telemetry."""

from __future__ import annotations

import pytest

from ghostshell.engine import BaseEngine, GhostResponse, PlaceholderEngine


def test_engine_inheritance() -> None:
    """Ensure PlaceholderEngine conforms to BaseEngine interface."""
    engine = PlaceholderEngine()
    assert isinstance(engine, BaseEngine)


def test_placeholder_engine_basic_prompt() -> None:
    """Verify response structure and diagnostics for a standard prompt."""
    engine = PlaceholderEngine()
    prompt = "How do I optimize a recursive function?"
    response = engine.process(prompt)

    assert isinstance(response, GhostResponse)
    assert response.prompt == prompt
    assert response.mode == "UI_DEV_PLACEHOLDER"
    assert response.status == "RECEPTIVE_STANDALONE"
    assert response.model_name == "Detached (Phase 1 UI Mode)"
    assert response.char_count == len(prompt)
    assert response.word_count == 7
    assert response.estimated_tokens > 0
    assert response.latency_ms >= 0.0
    assert response.execution_sandboxed is True


def test_placeholder_engine_no_fake_gemma() -> None:
    """Ensure requirement 8: Engine must NOT fake Gemma responses."""
    engine = PlaceholderEngine()
    prompt = "Tell me a story about a haunted computer"
    response = engine.process(prompt)

    # Content should explicitly announce UI Dev mode and detached weights
    assert "UI Development Mode Active" in response.content
    assert "detached" in response.content.lower()
    assert "Phase 2" in response.content
    # Must NOT pretend to be an LLM answering the prompt directly
    assert "As an AI model developed by Google" not in response.content
    assert "I am Gemma" not in response.content


def test_placeholder_engine_shell_command_notice() -> None:
    """Verify security containment notice when input looks like a shell command."""
    engine = PlaceholderEngine()
    for cmd in ["ls -la", "dir /w", "rm -rf test", "cat file.txt", "powershell -c echo"]:
        response = engine.process(cmd)
        assert response.metadata["shell_prefix_detected"] is True
        assert "Containment Notice" in response.content
        assert "forbids arbitrary command execution" in response.content


def test_placeholder_engine_empty_prompt() -> None:
    """Verify handling of empty or whitespace prompt."""
    engine = PlaceholderEngine()
    response = engine.process("   ")
    assert response.prompt == ""
    assert response.char_count == 0
    assert response.word_count == 0
    assert response.estimated_tokens == 0
