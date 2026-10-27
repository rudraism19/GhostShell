"""Unit tests for GhostShell response engines and telemetry."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.config import GhostConfig
from ghostshell.engine import BaseEngine, GemmaEngine, GhostResponse, PlaceholderEngine


def test_engine_inheritance() -> None:
    """Ensure PlaceholderEngine and GemmaEngine conform to BaseEngine interface."""
    assert isinstance(PlaceholderEngine(), BaseEngine)
    assert isinstance(GemmaEngine(), BaseEngine)


def test_placeholder_engine_basic_prompt() -> None:
    """Verify response structure and diagnostics for a standard prompt."""
    engine = PlaceholderEngine()
    prompt = "How do I optimize a recursive function?"
    response = engine.process(prompt)

    assert isinstance(response, GhostResponse)
    assert response.prompt == prompt
    assert response.mode == "UI_DEV_PLACEHOLDER"
    assert response.status == "RECEPTIVE_STANDALONE"
    assert "UI Dev Mode" in response.model_name
    assert response.char_count == len(prompt)
    assert response.word_count == 7
    assert response.estimated_tokens > 0
    assert response.latency_ms >= 0.0
    assert response.execution_sandboxed is True


def test_placeholder_engine_no_fake_gemma() -> None:
    """Ensure engine does NOT fake Gemma responses in placeholder mode."""
    engine = PlaceholderEngine()
    prompt = "Tell me a story about a haunted computer"
    response = engine.process(prompt)

    assert "UI Development Mode Active" in response.content
    assert "detached" in response.content.lower()
    assert "Phase 2" in response.content
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


def test_gemma_engine_successful_inference() -> None:
    """Verify GemmaEngine processes genuine responses from mocked client."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
    mock_client.chat_completion.return_value = CompletionResponse(
        content="Use memoization to avoid redundant subproblem calculations.",
        model="gemma-3-1b-it",
        prompt_tokens=22,
        completion_tokens=14,
        total_tokens=36,
        latency_ms=124.5,
    )

    config = GhostConfig()
    engine = GemmaEngine(client=mock_client, config=config)

    prompt = "How to memoize in Python?"
    response = engine.process(prompt)

    assert response.mode == "GEMMA_LOCAL"
    assert response.status == "ONLINE_BOUND"
    assert "memoization" in response.content
    assert "Gemma 3 1B" in response.model_name
    assert response.estimated_tokens == 36
    assert response.latency_ms == 124.5
    assert response.execution_sandboxed is True
    assert response.metadata["prompt_tokens"] == 22
    assert response.metadata["completion_tokens"] == 14


def test_gemma_engine_server_offline_graceful_fallback() -> None:
    """Requirement 6: Display clear, non-crashing error with instructions when server is down."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
    mock_client.model_name = "gemma-3-1b-it"
    mock_client.chat_completion.side_effect = ModelServerError(
        message="Connection refused",
        is_offline=True,
        endpoint="http://127.0.0.1:8080/v1/chat/completions",
    )

    engine = GemmaEngine(client=mock_client)
    prompt = "Review my git commit"
    response = engine.process(prompt)

    # Must NOT raise exception; returns structured offline response
    assert response.mode == "SERVER_OFFLINE"
    assert response.status == "CONDUIT_SEVERED"
    assert "llama-server" in response.content
    assert "gemma-3-1b-it-Q4_K_M.gguf" in response.content
    assert "8080" in response.content
    assert response.execution_sandboxed is True


def test_gemma_engine_shell_command_notice() -> None:
    """Verify security notice in GemmaEngine when user enters shell-like syntax."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
    mock_client.chat_completion.return_value = CompletionResponse(
        content="Here is explanation of directory listing.",
        model="gemma-3-1b-it",
        prompt_tokens=10,
        completion_tokens=10,
        total_tokens=20,
        latency_ms=50.0,
    )

    engine = GemmaEngine(client=mock_client)
    response = engine.process("dir /s")

    assert response.metadata["shell_prefix_detected"] is True
    assert "Security Notice" in response.content
    assert "strictly disabled" in response.content
