"""Unit tests for GhostShell slash commands and CommandHandler."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ghostshell.client import GemmaClient
from ghostshell.commands import CommandAction, CommandDoc, CommandHandler, CommandResult
from ghostshell.config import GhostConfig


@pytest.fixture
def handler() -> CommandHandler:
    """Fixture providing a fresh CommandHandler instance."""
    return CommandHandler()


def test_is_command(handler: CommandHandler) -> None:
    """Verify command detection prefix rules."""
    assert handler.is_command("/help") is True
    assert handler.is_command("/exit") is True
    assert handler.is_command("/status") is True
    assert handler.is_command("/model") is True
    assert handler.is_command("/custom") is True
    assert handler.is_command("  /spaced") is True

    # Non-commands
    assert handler.is_command("help") is False
    assert handler.is_command("ls -la") is False
    assert handler.is_command("dir") is False
    assert handler.is_command("echo hello") is False
    assert handler.is_command("") is False
    assert handler.is_command("   ") is False


def test_command_help_all(handler: CommandHandler) -> None:
    """Verify /help returns all registered command documentation."""
    result = handler.execute("/help")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "help_all"
    docs = result.data["docs"]
    assert len(docs) >= 6
    cmd_names = [d.name for d in docs]
    assert "/help" in cmd_names
    assert "/clear" in cmd_names
    assert "/exit" in cmd_names
    assert "/status" in cmd_names
    assert "/model" in cmd_names
    assert "/about" in cmd_names


def test_command_help_single(handler: CommandHandler) -> None:
    """Verify /help <command> returns documentation for a specific command."""
    result = handler.execute("/help model")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "help_single"
    doc: CommandDoc = result.data["doc"]
    assert doc.name == "/model"
    assert "/gemma" in doc.aliases


def test_command_clear(handler: CommandHandler) -> None:
    """Verify /clear returns CommandAction.CLEAR."""
    result = handler.execute("/clear")
    assert result.action == CommandAction.CLEAR
    assert "cleansed" in (result.message or "").lower()


def test_command_exit_and_quit(handler: CommandHandler) -> None:
    """Verify /exit, /quit, and /q signal session termination."""
    for cmd in ["/exit", "/quit", "/q"]:
        result = handler.execute(cmd)
        assert result.action == CommandAction.EXIT
        assert "released" in (result.message or "").lower()


def test_command_status_with_client_probe() -> None:
    """Verify /status probes model server health."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:8080/v1/chat/completions"
    mock_client.check_health.return_value = True

    h = CommandHandler(client=mock_client)
    res = h.execute("/status")

    assert res.action == CommandAction.CONTINUE
    info = res.data["info"]
    assert "ONLINE" in info["model_server"]
    assert "FORBIDDEN" in info["command_execution"]
    assert info["security_sandbox"] == "ACTIVE"


def test_command_status_offline_client() -> None:
    """Verify /status indicates when model server is offline."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.check_health.return_value = False

    h = CommandHandler(client=mock_client)
    res = h.execute("/status")

    info = res.data["info"]
    assert "OFFLINE" in info["model_server"]


def test_command_model(handler: CommandHandler) -> None:
    """Verify /model displays model configuration and target details."""
    result = handler.execute("/model")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "model_info"
    info = result.data["info"]
    assert "Model Name" in info
    assert "Local Endpoint" in info
    assert "Gemma 3 1B" in info["Quantization Target"]
    assert "8 GB RAM" in info["Target Hardware"]


def test_command_about(handler: CommandHandler) -> None:
    """Verify /about displays Ghost in the Machine challenge details."""
    result = handler.execute("/about")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "about"
    assert "Ghost in the Machine" in result.data["content"]
    assert "Gemma 3 1B" in result.data["content"]


def test_unknown_command(handler: CommandHandler) -> None:
    """Verify unknown slash commands return helpful spooky error messages."""
    result = handler.execute("/conjure_demon")
    assert result.action == CommandAction.ERROR
    assert "Unknown ritual" in (result.message or "")
    assert "/help" in (result.message or "")


def test_empty_command(handler: CommandHandler) -> None:
    """Verify bare slash returns an error."""
    result = handler.execute("/")
    assert result.action == CommandAction.ERROR
    assert "Empty command invocation" in (result.message or "")
