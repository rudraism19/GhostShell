"""Unit tests for newly added slash commands and Phase 4-7 functionality."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from ghostshell.client import CompletionResponse, GemmaClient
from ghostshell.commands import CommandAction, CommandHandler
from ghostshell.config import GhostConfig, is_local_endpoint
from ghostshell.engine import GemmaEngine
from ghostshell.git_intel import GitCommit, GitIntelligence, GitReviewResult, GitStoryResult, GitWorkingTreeStatus
from ghostshell.memory import GhostMemory
from ghostshell.persona import PersonaEngine
from ghostshell.ui import GhostUI


@pytest.fixture
def command_env(tmp_path: any) -> tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]:
    """Fixture providing a complete CommandHandler with mocked dependencies."""
    config = GhostConfig()
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.endpoint = "http://127.0.0.1:9931/v1/chat/completions"
    mock_client.model_name = "gemma-3-1b-it"
    mock_client.check_health.return_value = True

    memory = GhostMemory(data_dir=tmp_path / "test_mem", enabled=True)
    persona = PersonaEngine(default_persona="grim-debugger")
    git_intel = MagicMock(spec=GitIntelligence)
    git_intel.is_inside_work_tree.return_value = True
    git_intel.get_working_tree_status.return_value = GitWorkingTreeStatus(
        is_repo=True, branch="main", is_clean=True
    )

    handler = CommandHandler(
        config=config,
        client=mock_client,
        git_intel=git_intel,
        memory=memory,
        persona_engine=persona,
    )
    return handler, memory, persona, mock_client, git_intel


def test_command_git(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /git command returns recent commits."""
    handler, _, _, _, git_intel = command_env
    git_intel.get_recent_commits.return_value = [
        GitCommit(hash="1111111", author="A", date="today", message="M1"),
        GitCommit(hash="2222222", author="B", date="yesterday", message="M2"),
    ]

    res = handler.execute("/git 2")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "git_commits"
    assert len(res.data["commits"]) == 2
    assert res.data["commits"][0].hash == "1111111"


def test_command_story(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /story command summons a gothic tale."""
    handler, _, _, _, git_intel = command_env
    git_intel.generate_story.return_value = GitStoryResult(
        story="A tale of machine ghosts...",
        commits_used=[GitCommit(hash="abc", author="X", date="now", message="Commit")],
        mode="GEMMA_LOCAL",
    )

    res = handler.execute("/story")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "git_story"
    assert "tale of machine ghosts" in res.data["result"].story


def test_command_review(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /review command returns cautious development analysis."""
    handler, _, _, _, git_intel = command_env
    git_intel.generate_review.return_value = GitReviewResult(
        review="Steady velocity with clean tree.",
        commits_analyzed=3,
        working_tree_clean=True,
    )

    res = handler.execute("/review")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "git_review"
    assert "Steady velocity" in res.data["result"].review


def test_command_githelp(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /githelp displays Git intelligence rites guide."""
    handler, _, _, _, _ = command_env
    res = handler.execute("/githelp")
    assert res.action == CommandAction.CONTINUE
    assert "Git Intelligence Rites" in res.message
    assert "/git" in res.message
    assert "/story" in res.message


def test_command_history(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /history command displays stored conversation turns."""
    handler, memory, _, _, _ = command_env
    memory.record_turn("Prompt A", "Answer A")

    res = handler.execute("/history")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "memory_history"
    assert len(res.data["entries"]) == 2


def test_command_forget(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /forget command purges persistent memory."""
    handler, memory, _, _, _ = command_env
    memory.record_turn("Prompt", "Answer")

    res = handler.execute("/forget")
    assert res.action == CommandAction.CONTINUE
    assert "purged" in res.message.lower()
    assert len(memory.get_history()) == 0


def test_command_storage(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /storage command returns storage and privacy metadata."""
    handler, _, _, _, _ = command_env
    res = handler.execute("/storage")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "storage_diagnostics"
    assert res.data["info"]["enabled"] is True


def test_command_persona(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /persona command to inspect and change archetypes."""
    handler, _, persona, _, _ = command_env

    # Without arguments, inspect status
    res = handler.execute("/persona")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "persona_status"

    # With valid argument, shift persona
    res = handler.execute("/persona poltergeist")
    assert res.action == CommandAction.CONTINUE
    assert persona.current_persona.name == "poltergeist"
    assert "Poltergeist" in res.message

    # With invalid argument, return error with suggestions
    res = handler.execute("/persona werewolf")
    assert res.action == CommandAction.ERROR
    assert "Unknown archetype" in res.message


def test_command_theme(command_env: tuple[CommandHandler, GhostMemory, PersonaEngine, MagicMock, GitIntelligence]) -> None:
    """Test /theme command to inspect and shift color themes."""
    handler, _, persona, _, _ = command_env

    res = handler.execute("/theme")
    assert res.action == CommandAction.CONTINUE
    assert "Active theme" in res.message

    res = handler.execute("/theme amber")
    assert res.action == CommandAction.CONTINUE
    assert res.data["type"] == "theme_changed"
    assert persona.current_theme.name == "amber"

    res = handler.execute("/theme neon-invalid")
    assert res.action == CommandAction.ERROR
    assert "Unknown theme" in res.message


def test_is_local_endpoint_detection() -> None:
    """Verify local vs external endpoint classification for privacy guards."""
    assert is_local_endpoint("http://127.0.0.1:9931/v1/chat/completions") is True
    assert is_local_endpoint("http://localhost:8080/v1/chat/completions") is True
    assert is_local_endpoint("http://0.0.0.0:8000/v1/chat/completions") is True

    # External endpoints must be flagged
    assert is_local_endpoint("https://api.openai.com/v1/chat/completions") is False
    assert is_local_endpoint("https://cloud.groq.com/openai/v1/chat/completions") is False
    assert is_local_endpoint("http://192.168.1.50:8080/v1/chat/completions") is False


def test_gemma_engine_memory_context_injection(tmp_path: any) -> None:
    """Verify GemmaEngine injects prior context pairs into local model requests."""
    mock_client = MagicMock(spec=GemmaClient)
    mock_client.chat_completion.return_value = CompletionResponse(
        content="Understood.",
        model="gemma-3-1b-it",
        prompt_tokens=30,
        completion_tokens=5,
        total_tokens=35,
        latency_ms=45.0,
    )
    mock_client.endpoint = "http://127.0.0.1:9931/v1/chat/completions"

    memory = GhostMemory(data_dir=tmp_path / "eng_mem", enabled=True)
    memory.record_turn("I am building an OS", "Fascinating work.")

    persona = PersonaEngine(default_persona="archivist")
    config = GhostConfig()
    engine = GemmaEngine(
        client=mock_client,
        config=config,
        persona_engine=persona,
        memory=memory,
    )

    resp = engine.process("What was I building?")
    assert resp.mode == "GEMMA_LOCAL"

    # Verify messages passed to chat_completion
    call_args = mock_client.chat_completion.call_args[0][0]
    # system, user (past), assistant (past), user (current)
    assert len(call_args) == 4
    assert call_args[0]["role"] == "system"
    assert "The Archivist" in call_args[0]["content"]
    assert call_args[1]["content"] == "I am building an OS"
    assert call_args[2]["content"] == "Fascinating work."
    assert call_args[3]["content"] == "What was I building?"
