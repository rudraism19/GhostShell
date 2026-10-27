"""Unit tests for GhostShell Git Intelligence subsystem (Phase 4)."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from ghostshell.client import CompletionResponse, GemmaClient, ModelServerError
from ghostshell.git_intel import (
    GitCommit,
    GitIntelligence,
    GitReviewResult,
    GitStoryResult,
    GitWorkingTreeStatus,
)


@pytest.fixture
def git_service() -> GitIntelligence:
    """Fixture providing a GitIntelligence instance."""
    return GitIntelligence(repo_dir="/mock/repo")


def test_is_inside_work_tree_true(git_service: GitIntelligence) -> None:
    """Verify is_inside_work_tree returns True when git confirms repository."""
    mock_res = subprocess.CompletedProcess(args=[], returncode=0, stdout="true", stderr="")
    with patch("subprocess.run", return_value=mock_res) as mock_run:
        assert git_service.is_inside_work_tree() is True
        mock_run.assert_called_once()
        assert mock_run.call_args[1]["shell"] is False


def test_is_inside_work_tree_false(git_service: GitIntelligence) -> None:
    """Verify is_inside_work_tree returns False outside a git repo."""
    mock_res = subprocess.CompletedProcess(args=[], returncode=128, stdout="", stderr="fatal: not a git repo")
    with patch("subprocess.run", return_value=mock_res):
        assert git_service.is_inside_work_tree() is False


def test_git_missing_on_path(git_service: GitIntelligence) -> None:
    """Verify graceful handling when git executable is not on system PATH."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        commits = git_service.get_recent_commits()
        assert commits == []
        status = git_service.get_working_tree_status()
        assert status.is_repo is False
        assert "not a Git repository" in status.error_message


def test_git_subprocess_timeout(git_service: GitIntelligence) -> None:
    """Verify subprocess timeout is caught safely without hanging."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5.0)):
        assert git_service.is_inside_work_tree() is False
        commits = git_service.get_recent_commits()
        assert commits == []


def test_get_recent_commits_parsing(git_service: GitIntelligence) -> None:
    """Verify parsing of formatted git log output."""
    mock_log_output = (
        "a17108a|GhostShell Dev|10 minutes ago|Implement Phase 3: Possessed Java Debugger\n"
        "630e3c4|GhostShell Dev|2 hours ago|Implement Phase 2: Local Gemma 3 1B integration\n"
        "a7615fc|GhostShell Dev|1 day ago|Implement Phase 1: GhostShell terminal UI"
    )

    with patch.object(git_service, "is_inside_work_tree", return_value=True):
        mock_res = subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_log_output, stderr="")
        with patch("subprocess.run", return_value=mock_res) as mock_run:
            commits = git_service.get_recent_commits(limit=3)

            assert len(commits) == 3
            assert commits[0].hash == "a17108a"
            assert commits[0].author == "GhostShell Dev"
            assert "Phase 3" in commits[0].message
            assert commits[1].hash == "630e3c4"
            assert commits[2].hash == "a7615fc"
            # Ensure safe argument array
            args_passed = mock_run.call_args[0][0]
            assert "git" in args_passed
            assert "log" in args_passed
            assert mock_run.call_args[1]["shell"] is False


def test_get_working_tree_status_clean(git_service: GitIntelligence) -> None:
    """Verify clean working tree detection."""
    with patch.object(git_service, "is_inside_work_tree", return_value=True):
        with patch.object(git_service, "get_current_branch", return_value="main"):
            mock_res = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            with patch("subprocess.run", return_value=mock_res):
                status = git_service.get_working_tree_status()
                assert status.is_repo is True
                assert status.branch == "main"
                assert status.is_clean is True
                assert len(status.staged_files) == 0
                assert len(status.unstaged_files) == 0
                assert len(status.untracked_files) == 0


def test_get_working_tree_status_dirty(git_service: GitIntelligence) -> None:
    """Verify dirty working tree with staged, modified, and untracked files."""
    porcelain_output = (
        "M  ghostshell/git_intel.py\n"
        " M main.py\n"
        "?? tests/test_git_intel.py"
    )

    with patch.object(git_service, "is_inside_work_tree", return_value=True):
        with patch.object(git_service, "get_current_branch", return_value="feature/git-lore"):
            mock_res = subprocess.CompletedProcess(args=[], returncode=0, stdout=porcelain_output, stderr="")
            with patch("subprocess.run", return_value=mock_res):
                status = git_service.get_working_tree_status()
                assert status.is_clean is False
                assert status.branch == "feature/git-lore"
                assert "ghostshell/git_intel.py" in status.staged_files
                assert "main.py" in status.unstaged_files
                assert "tests/test_git_intel.py" in status.untracked_files


def test_generate_story_with_mocked_gemma(git_service: GitIntelligence) -> None:
    """Verify story generation using local Gemma client."""
    mock_commits = [
        GitCommit(hash="abc1234", author="Dev", date="1 hour ago", message="Add cursed loop"),
        GitCommit(hash="def5678", author="Dev", date="2 hours ago", message="Exorcise null pointer"),
    ]

    mock_client = MagicMock(spec=GemmaClient)
    mock_client.chat_completion.return_value = CompletionResponse(
        content="In the quiet depths of memory, commit abc1234 stirred...",
        model="gemma-3-1b-it",
        prompt_tokens=50,
        completion_tokens=40,
        total_tokens=90,
        latency_ms=110.0,
    )

    with patch.object(git_service, "get_recent_commits", return_value=mock_commits):
        result = git_service.generate_story(
            client=mock_client,
            system_prompt="You are a machine ghost",
            limit=2,
        )

        assert isinstance(result, GitStoryResult)
        assert result.mode == "GEMMA_LOCAL"
        assert "abc1234" in result.story
        assert len(result.commits_used) == 2
        assert result.latency_ms == 110.0


def test_generate_story_offline_fallback(git_service: GitIntelligence) -> None:
    """Verify story offline fallback when Gemma client is offline or raises ModelServerError."""
    mock_commits = [
        GitCommit(hash="abc1234", author="Mortal", date="yesterday", message="Initial spark"),
    ]

    mock_client = MagicMock(spec=GemmaClient)
    mock_client.chat_completion.side_effect = ModelServerError(message="Offline", is_offline=True)

    with patch.object(git_service, "get_recent_commits", return_value=mock_commits):
        result = git_service.generate_story(
            client=mock_client,
            system_prompt="Ghost prompt",
            limit=1,
        )

        assert result.mode == "GROUNDED_OFFLINE_FALLBACK"
        assert "abc1234" in result.story
        assert "Initial spark" in result.story


def test_generate_review_with_mocked_gemma(git_service: GitIntelligence) -> None:
    """Verify code review generation using local Gemma client."""
    mock_commits = [
        GitCommit(hash="1234567", author="Dev", date="just now", message="Fix loop condition"),
    ]
    mock_tree = GitWorkingTreeStatus(is_repo=True, branch="main", is_clean=True)

    mock_client = MagicMock(spec=GemmaClient)
    mock_client.chat_completion.return_value = CompletionResponse(
        content="Activity review: High commit velocity with clean tree.",
        model="gemma-3-1b-it",
        prompt_tokens=40,
        completion_tokens=30,
        total_tokens=70,
        latency_ms=85.0,
    )

    with patch.object(git_service, "get_recent_commits", return_value=mock_commits):
        with patch.object(git_service, "get_working_tree_status", return_value=mock_tree):
            res = git_service.generate_review(
                client=mock_client,
                system_prompt="Grim debugger prompt",
                limit=1,
            )

            assert isinstance(res, GitReviewResult)
            assert res.mode == "GEMMA_LOCAL"
            assert "clean tree" in res.review
            assert res.working_tree_clean is True
            assert "strictly in recent commit subjects" in res.grounded_disclaimer


def test_generate_review_offline_fallback(git_service: GitIntelligence) -> None:
    """Verify code review offline fallback when client is None."""
    mock_commits = [
        GitCommit(hash="1234567", author="Dev", date="just now", message="Fix loop condition"),
    ]
    mock_tree = GitWorkingTreeStatus(is_repo=True, branch="main", is_clean=False, staged_files=["a.py"])

    with patch.object(git_service, "get_recent_commits", return_value=mock_commits):
        with patch.object(git_service, "get_working_tree_status", return_value=mock_tree):
            res = git_service.generate_review(
                client=None,
                system_prompt="Grim prompt",
                limit=1,
            )

            assert res.mode == "GROUNDED_OFFLINE_FALLBACK"
            assert "1234567" in res.review
            assert "restless" in res.review.lower()
