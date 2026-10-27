"""Unit tests for the modular GemmaClient using mocked HTTP responses."""

from __future__ import annotations

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError


def _mock_http_response(status: int, body_dict: dict) -> MagicMock:
    """Helper creating a mock HTTP response object."""
    mock = MagicMock()
    mock.status = status
    mock.read.return_value = json.dumps(body_dict).encode("utf-8")
    mock.__enter__.return_value = mock
    mock.__exit__.return_value = None
    return mock


def test_client_chat_completion_success() -> None:
    """Verify parsing of valid OpenAI-compatible completion response."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions", model_name="gemma-3-1b-it")

    mock_resp_data = {
        "model": "gemma-3-1b-it",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "👻 Mortal coder, your syntax has angered the silicon spirits!",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 20,
            "total_tokens": 35,
        },
    }

    with patch("urllib.request.urlopen", return_value=_mock_http_response(200, mock_resp_data)):
        messages = [{"role": "user", "content": "Why is my pointer null?"}]
        res = client.chat_completion(messages)

    assert isinstance(res, CompletionResponse)
    assert "Mortal coder" in res.content
    assert res.model == "gemma-3-1b-it"
    assert res.prompt_tokens == 15
    assert res.completion_tokens == 20
    assert res.total_tokens == 35
    assert res.latency_ms >= 0.0


def test_client_server_offline() -> None:
    """Verify ModelServerError is raised with is_offline=True when connection fails."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        with pytest.raises(ModelServerError) as exc_info:
            client.chat_completion([{"role": "user", "content": "Hello"}])

    assert exc_info.value.is_offline is True
    assert "Unable to connect" in exc_info.value.message


def test_client_server_timeout() -> None:
    """Verify timeout triggers ModelServerError with is_offline=True."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    with patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out")):
        with pytest.raises(ModelServerError) as exc_info:
            client.chat_completion([{"role": "user", "content": "Hello"}])

    assert exc_info.value.is_offline is True


def test_client_http_500_error() -> None:
    """Verify HTTP errors raise ModelServerError with status code."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    mock_err = urllib.error.HTTPError(
        url="http://127.0.0.1:8080/v1/chat/completions",
        code=500,
        msg="Internal Server Error",
        hdrs=MagicMock(),
        fp=io.BytesIO(b"Gemma context exhausted"),
    )

    with patch("urllib.request.urlopen", side_effect=mock_err):
        with pytest.raises(ModelServerError) as exc_info:
            client.chat_completion([{"role": "user", "content": "Overflow"}])

    assert exc_info.value.status_code == 500
    assert exc_info.value.is_offline is False


def test_client_malformed_json() -> None:
    """Verify handling of invalid JSON from server."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"<html>Not JSON</html>"
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(ModelServerError) as exc_info:
            client.chat_completion([{"role": "user", "content": "Hello"}])

    assert "Invalid JSON" in exc_info.value.message


def test_client_check_health_online() -> None:
    """Verify check_health returns True when server responds."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert client.check_health() is True


def test_client_check_health_offline() -> None:
    """Verify check_health returns False when server connection fails."""
    client = GemmaClient(endpoint="http://127.0.0.1:8080/v1/chat/completions")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Refused")):
        assert client.check_health() is False
