"""Unit tests for GhostShell slash commands and CommandHandler."""

from __future__ import annotations

import pytest

from ghostshell.commands import CommandAction, CommandDoc, CommandHandler, CommandResult


@pytest.fixture
def handler() -> CommandHandler:
    """Fixture providing a fresh CommandHandler instance."""
    return CommandHandler()


def test_is_command(handler: CommandHandler) -> None:
    """Verify command detection prefix rules."""
    assert handler.is_command("/help") is True
    assert handler.is_command("/exit") is True
    assert handler.is_command("/status") is True
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
    assert len(docs) >= 5
    cmd_names = [d.name for d in docs]
    assert "/help" in cmd_names
    assert "/clear" in cmd_names
    assert "/exit" in cmd_names
    assert "/status" in cmd_names
    assert "/about" in cmd_names


def test_command_help_single(handler: CommandHandler) -> None:
    """Verify /help <command> returns documentation for a specific command."""
    result = handler.execute("/help clear")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "help_single"
    doc: CommandDoc = result.data["doc"]
    assert doc.name == "/clear"
    assert "/cls" in doc.aliases


def test_command_help_invalid_subcommand(handler: CommandHandler) -> None:
    """Verify /help <unknown> returns an error."""
    result = handler.execute("/help non_existent_spell")
    assert result.action == CommandAction.ERROR
    assert "No grimoire entry found" in (result.message or "")


def test_command_clear(handler: CommandHandler) -> None:
    """Verify /clear returns CommandAction.CLEAR."""
    result = handler.execute("/clear")
    assert result.action == CommandAction.CLEAR
    assert "cleansed" in (result.message or "").lower()

    # Test alias /cls
    result_alias = handler.execute("/cls")
    assert result_alias.action == CommandAction.CLEAR


def test_command_exit_and_quit(handler: CommandHandler) -> None:
    """Verify /exit, /quit, and /q signal session termination."""
    for cmd in ["/exit", "/quit", "/q"]:
        result = handler.execute(cmd)
        assert result.action == CommandAction.EXIT
        assert "released" in (result.message or "").lower()


def test_command_status(handler: CommandHandler) -> None:
    """Verify /status returns system and containment diagnostic information."""
    result = handler.execute("/status")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "status"
    info = result.data["info"]
    assert info["version"] == "0.1.0"
    assert "PlaceholderEngine" in info["engine"]
    assert "FORBIDDEN" in info["command_execution"]
    assert info["security_sandbox"] == "ACTIVE"


def test_command_about(handler: CommandHandler) -> None:
    """Verify /about displays Ghost in the Machine challenge details."""
    result = handler.execute("/about")
    assert result.action == CommandAction.CONTINUE
    assert result.data is not None
    assert result.data["type"] == "about"
    assert "Ghost in the Machine" in result.data["content"]
    assert "local-first" in result.data["content"].lower()


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


def test_non_command_passed_to_execute(handler: CommandHandler) -> None:
    """Verify passing text without slash returns error action."""
    result = handler.execute("hello ghost")
    assert result.action == CommandAction.ERROR
    assert "Not a slash command" in (result.message or "")


def test_custom_command_registration(handler: CommandHandler) -> None:
    """Verify extensible command registry for future phases."""
    def _my_spell(args: list[str]) -> CommandResult:
        return CommandResult(
            action=CommandAction.CONTINUE,
            message=f"Cast spell with args: {args}",
        )

    handler.register(
        name="spell",
        handler=_my_spell,
        doc=CommandDoc(
            name="/spell",
            description="Cast a custom hex.",
            usage="/spell <arg>",
            aliases=["/hex"],
        ),
    )

    res = handler.execute("/spell lightning")
    assert res.action == CommandAction.CONTINUE
    assert res.message == "Cast spell with args: ['lightning']"

    # Test alias
    res_alias = handler.execute("/hex frost")
    assert res_alias.action == CommandAction.CONTINUE
    assert res_alias.message == "Cast spell with args: ['frost']"
