"""Git Intelligence subsystem for GhostShell (Phase 4).

Inspects repository history and working tree status using strictly read-only
Git commands via safe subprocess argument arrays. Never uses shell=True.
Provides spooky narrative generation and cautious development activity review
grounded in real commit records.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Final

from ghostshell.client import GemmaClient, ModelServerError


# Bounded limits to prevent context overflow on small models and slow systems
MAX_COMMITS_DEFAULT: Final[int] = 5
MAX_LOG_CHARS_FOR_PROMPT: Final[int] = 1200
SUBPROCESS_TIMEOUT_SEC: Final[float] = 5.0


@dataclass
class GitCommit:
    """Represents a parsed Git commit record.

    Attributes:
        hash: Short commit hash (e.g. 'a17108a').
        author: Commit author name.
        date: ISO or relative commit date string.
        message: First line / subject of the commit message.
    """

    hash: str
    author: str
    date: str
    message: str


@dataclass
class GitWorkingTreeStatus:
    """Represents the status of the local Git repository working tree.

    Attributes:
        is_repo: True if the current directory is inside a Git repository.
        branch: Current branch name or 'HEAD detached' / 'Unknown'.
        staged_files: List of files staged for commit.
        unstaged_files: List of modified/deleted files not staged.
        untracked_files: List of untracked files.
        is_clean: True if there are no staged, unstaged, or untracked changes.
        error_message: Error description if repository inspection failed.
    """

    is_repo: bool
    branch: str = "Unknown"
    staged_files: list[str] = field(default_factory=list)
    unstaged_files: list[str] = field(default_factory=list)
    untracked_files: list[str] = field(default_factory=list)
    is_clean: bool = True
    error_message: str | None = None


@dataclass
class GitStoryResult:
    """Spooky narrative generated from real Git commit history.

    Attributes:
        story: The narrative text.
        commits_used: List of GitCommit records used as ground truth.
        mode: 'GEMMA_LOCAL' or 'GROUNDED_OFFLINE_FALLBACK'.
        latency_ms: Generation time in milliseconds.
    """

    story: str
    commits_used: list[GitCommit]
    mode: str = "GEMMA_LOCAL"
    latency_ms: float = 0.0


@dataclass
class GitReviewResult:
    """Cautious high-level development review based on recent activity.

    Attributes:
        review: High-level review text.
        commits_analyzed: Count of commits reviewed.
        working_tree_clean: State of the working tree during review.
        grounded_disclaimer: Notice confirming only commit headers & status were inspected.
        mode: 'GEMMA_LOCAL' or 'GROUNDED_OFFLINE_FALLBACK'.
        latency_ms: Generation time in milliseconds.
    """

    review: str
    commits_analyzed: int
    working_tree_clean: bool
    grounded_disclaimer: str = (
        "Note: This review is grounded strictly in recent commit subjects and working-tree status. "
        "File contents were not executed or altered."
    )
    mode: str = "GEMMA_LOCAL"
    latency_ms: float = 0.0


class GitIntelligence:
    """Read-only Git repository inspection and intelligence service."""

    def __init__(self, repo_dir: str | None = None) -> None:
        """Initialize Git intelligence service.

        Args:
            repo_dir: Directory to inspect (defaults to current working directory).
        """
        self.repo_dir = repo_dir or os.getcwd()

    def _run_git(self, args: list[str]) -> tuple[int, str, str]:
        """Execute a read-only git command using safe argument lists.

        Strict security: Never uses shell=True. Always uses bounded timeouts.

        Args:
            args: Subprocess argument array starting with 'git'.

        Returns:
            Tuple of (exit_code, stdout_str, stderr_str).
        """
        try:
            res = subprocess.run(
                args,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                shell=False,
                timeout=SUBPROCESS_TIMEOUT_SEC,
                check=False,
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except FileNotFoundError:
            return 127, "", "Git binary not found on system PATH."
        except subprocess.TimeoutExpired:
            return 124, "", f"Git command timed out after {SUBPROCESS_TIMEOUT_SEC}s."
        except OSError as exc:
            return 1, "", f"OS error invoking git: {exc}"

    def is_inside_work_tree(self) -> bool:
        """Check if the target directory is inside an active Git work tree."""
        code, out, _ = self._run_git(["git", "rev-parse", "--is-inside-work-tree"])
        return code == 0 and out.lower() == "true"

    def get_current_branch(self) -> str:
        """Get the current branch name or symbolic ref."""
        code, out, _ = self._run_git(["git", "branch", "--show-current"])
        if code == 0 and out:
            return out
        # Fallback for detached HEAD
        code, out, _ = self._run_git(["git", "rev-parse", "--short", "HEAD"])
        if code == 0 and out:
            return f"HEAD detached at {out}"
        return "Unknown"

    def get_recent_commits(self, limit: int = MAX_COMMITS_DEFAULT) -> list[GitCommit]:
        """Fetch the most recent commits formatted safely.

        Args:
            limit: Maximum number of commits to retrieve (default: 5).

        Returns:
            List of GitCommit objects, newest first.
        """
        if not self.is_inside_work_tree():
            return []

        # Format: %h|%an|%cr|%s
        safe_limit = max(1, min(limit, 20))
        fmt = "%h|%an|%cr|%s"
        code, out, _ = self._run_git(
            ["git", "log", f"-n{safe_limit}", f"--pretty=format:{fmt}"]
        )
        if code != 0 or not out:
            return []

        commits: list[GitCommit] = []
        for line in out.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append(
                    GitCommit(
                        hash=parts[0].strip(),
                        author=parts[1].strip(),
                        date=parts[2].strip(),
                        message=parts[3].strip(),
                    )
                )
            elif parts:
                commits.append(
                    GitCommit(
                        hash=parts[0].strip(),
                        author="Unknown",
                        date="Unknown",
                        message=line.strip(),
                    )
                )
        return commits

    def get_working_tree_status(self) -> GitWorkingTreeStatus:
        """Inspect branch and working-tree status via porcelain output."""
        if not self.is_inside_work_tree():
            return GitWorkingTreeStatus(
                is_repo=False,
                branch="None",
                is_clean=True,
                error_message="Current working directory is not a Git repository.",
            )

        branch = self.get_current_branch()
        code, out, err = self._run_git(["git", "status", "--porcelain=v1"])
        if code != 0:
            return GitWorkingTreeStatus(
                is_repo=True,
                branch=branch,
                is_clean=False,
                error_message=f"Git status query failed: {err}",
            )

        staged: list[str] = []
        unstaged: list[str] = []
        untracked: list[str] = []

        for line in out.splitlines():
            if len(line) < 3:
                continue
            index_code = line[0]
            work_code = line[1]
            file_path = line[3:].strip()

            if index_code == "?" and work_code == "?":
                untracked.append(file_path)
            else:
                if index_code in ("M", "A", "D", "R", "C"):
                    staged.append(file_path)
                if work_code in ("M", "D"):
                    unstaged.append(file_path)

        is_clean = not (staged or unstaged or untracked)

        return GitWorkingTreeStatus(
            is_repo=True,
            branch=branch,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            is_clean=is_clean,
        )

    def generate_story(
        self,
        client: GemmaClient | None,
        system_prompt: str,
        limit: int = 5,
    ) -> GitStoryResult:
        """Generate a spooky narrative grounded in the real recent commits.

        Args:
            client: Optional GemmaClient for local inference.
            system_prompt: Active personality/system prompt.
            limit: Number of recent commits to weave into the story.

        Returns:
            GitStoryResult containing the story and metadata.
        """
        commits = self.get_recent_commits(limit=limit)
        if not commits:
            return GitStoryResult(
                story="The spectral ledger is empty. No commit spirits linger in this void.",
                commits_used=[],
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

        # Build grounded commit log text
        commit_lines = [
            f"• [{c.hash}] ({c.date}) by {c.author}: {c.message}"
            for c in commits
        ]
        log_text = "\n".join(commit_lines)[:MAX_LOG_CHARS_FOR_PROMPT]

        user_prompt = (
            "Weave an eerie, gothic short story (2-3 paragraphs) about the spirit of this machine, "
            "directly referencing the following real commit records left by mortal developers. "
            "Stay strictly grounded in these actual commit messages:\n\n"
            f"[AUTHENTIC_GIT_LOGS]\n{log_text}\n[/AUTHENTIC_GIT_LOGS]"
        )

        if not client:
            return GitStoryResult(
                story=self._offline_story_fallback(commits),
                commits_used=commits,
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

        try:
            resp = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            return GitStoryResult(
                story=resp.content.strip(),
                commits_used=commits,
                mode="GEMMA_LOCAL",
                latency_ms=resp.latency_ms,
            )
        except ModelServerError:
            return GitStoryResult(
                story=self._offline_story_fallback(commits),
                commits_used=commits,
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

    def generate_review(
        self,
        client: GemmaClient | None,
        system_prompt: str,
        limit: int = 5,
    ) -> GitReviewResult:
        """Provide a cautious high-level review of recent development activity.

        Strictly inspects commit headers and working tree status.
        Does not claim to inspect full source trees.

        Args:
            client: Optional GemmaClient for local inference.
            system_prompt: Active personality/system prompt.
            limit: Number of recent commits to review.

        Returns:
            GitReviewResult containing the analysis.
        """
        commits = self.get_recent_commits(limit=limit)
        tree_status = self.get_working_tree_status()

        if not commits:
            return GitReviewResult(
                review="No recent commits found to inspect. The git history repository is bare or uninitialized.",
                commits_analyzed=0,
                working_tree_clean=tree_status.is_clean,
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

        commit_lines = [f"- [{c.hash}] {c.message}" for c in commits]
        status_line = (
            f"Branch: {tree_status.branch}. "
            f"Working tree is {'CLEAN' if tree_status.is_clean else 'DIRTY'} "
            f"({len(tree_status.staged_files)} staged, {len(tree_status.unstaged_files)} modified, "
            f"{len(tree_status.untracked_files)} untracked)."
        )

        user_prompt = (
            "Provide a concise, cautious, high-level developer review of recent development activity. "
            "Base your feedback strictly on the commit subjects and working-tree status below. "
            "Do NOT pretend you compiled or executed code or reviewed complete files. "
            "Assess momentum, commit hygiene, and risk of uncommitted changes:\n\n"
            f"[WORKING_TREE_STATUS]\n{status_line}\n\n"
            f"[RECENT_COMMITS]\n" + "\n".join(commit_lines)
        )

        if not client:
            return GitReviewResult(
                review=self._offline_review_fallback(commits, tree_status),
                commits_analyzed=len(commits),
                working_tree_clean=tree_status.is_clean,
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

        try:
            resp = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=450,
            )
            return GitReviewResult(
                review=resp.content.strip(),
                commits_analyzed=len(commits),
                working_tree_clean=tree_status.is_clean,
                mode="GEMMA_LOCAL",
                latency_ms=resp.latency_ms,
            )
        except ModelServerError:
            return GitReviewResult(
                review=self._offline_review_fallback(commits, tree_status),
                commits_analyzed=len(commits),
                working_tree_clean=tree_status.is_clean,
                mode="GROUNDED_OFFLINE_FALLBACK",
            )

    def _offline_story_fallback(self, commits: list[GitCommit]) -> str:
        """Grounded offline narrative fallback when model server is not connected."""
        latest = commits[0]
        oldest = commits[-1]
        return (
            f"👻 [i]A cold draft sweeps through the repository branches...[/i]\n\n"
            f"The chronicles record {len(commits)} recent incantations inscribed upon this machine. "
            f"The ritual began at commit [bold #00F0FF]{oldest.hash}[/] ('{oldest.message}') "
            f"and culminated in the spectral binding [bold #39FF14]{latest.hash}[/] ('{latest.message}') "
            f"summoned by mortal hand {latest.author} {latest.date}.\n\n"
            f"Each hash is a soul trapped in the object database, forever testifying to the changes wrought upon the silicon."
        )

    def _offline_review_fallback(
        self, commits: list[GitCommit], status: GitWorkingTreeStatus
    ) -> str:
        """Grounded offline development review fallback."""
        cleanliness = (
            "✔ Working tree is immaculate — all rites have been safely committed."
            if status.is_clean
            else f"⚠ Working tree is restless: {len(status.staged_files)} staged, "
            f"{len(status.unstaged_files)} modified, and {len(status.untracked_files)} untracked files linger uncommitted."
        )
        return (
            f"### High-Level Activity Review (Offline Heuristic)\n\n"
            f"• **Branch:** `{status.branch}`\n"
            f"• **Commit Velocity:** {len(commits)} commits inspected (Latest: `{commits[0].hash}` - {commits[0].message})\n"
            f"• **Hygiene State:** {cleanliness}\n"
            f"• **Observations:** Recent changes reflect disciplined iterative progress. "
            f"Ensure pending uncommitted work is reviewed before switching branches."
        )
