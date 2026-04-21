"""R2E-Gym-inspired local Git commit discovery helpers.

This is intentionally heuristic and local-first. It does not import R2E-Gym's
hardcoded repo registry or runtime.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from taskforge.config import is_agent_instruction_file, is_code_file


class CommitCandidate(BaseModel):
    repo_path: str
    commit: str
    parent: str = ""
    title: str = ""
    files: list[str] = Field(default_factory=list)
    code_files: list[str] = Field(default_factory=list)
    test_files: list[str] = Field(default_factory=list)
    agent_instruction_files: list[str] = Field(default_factory=list)

    @property
    def has_code_and_tests(self) -> bool:
        return bool(self.code_files and self.test_files)

    @property
    def has_agent_instruction_context(self) -> bool:
        return bool(self.agent_instruction_files)

    @property
    def score(self) -> int:
        score = 0
        if self.has_code_and_tests:
            score += 4
        if self.has_agent_instruction_context:
            score += 5
        if 1 <= len(self.code_files) <= 5:
            score += 2
        if len(self.files) <= 12:
            score += 1
        return score


def inspect_commit(repo_path: str | Path, commit: str) -> CommitCandidate:
    """Inspect one local Git commit and return a ranked candidate summary."""

    repo = Path(repo_path)
    title = _git(repo, ["show", "-s", "--format=%s", commit]).strip()
    parent = _git(repo, ["rev-parse", f"{commit}^"], allow_error=True).strip()
    files = [
        line.strip()
        for line in _git(
            repo, ["diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit]
        ).splitlines()
        if line.strip()
    ]
    code_files = [path for path in files if is_code_file(path)]
    test_files = [path for path in files if _is_test_path(path)]
    agent_files = [path for path in files if is_agent_instruction_file(path)]
    return CommitCandidate(
        repo_path=str(repo),
        commit=commit,
        parent=parent,
        title=title,
        files=files,
        code_files=code_files,
        test_files=test_files,
        agent_instruction_files=agent_files,
    )


def discover_recent_commits(
    repo_path: str | Path, *, limit: int = 100
) -> list[CommitCandidate]:
    """Return recent commits ranked by taskforge usefulness."""

    repo = Path(repo_path)
    hashes = [
        line.strip()
        for line in _git(
            repo, ["rev-list", f"--max-count={limit}", "HEAD"]
        ).splitlines()
        if line.strip()
    ]
    candidates = [inspect_commit(repo, commit) for commit in hashes]
    return sorted(candidates, key=lambda item: item.score, reverse=True)


def _is_test_path(path: str) -> bool:
    lower = path.lower()
    return (
        "/test/" in lower
        or "/tests/" in lower
        or lower.startswith("test/")
        or lower.startswith("tests/")
        or lower.endswith("_test.py")
        or lower.endswith(".test.ts")
        or lower.endswith(".test.tsx")
        or lower.endswith(".spec.ts")
        or lower.endswith(".spec.tsx")
        or lower.endswith("_test.go")
        or lower.endswith("_test.rs")
    )


def _git(repo: Path, args: list[str], *, allow_error: bool = False) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not allow_error:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout
