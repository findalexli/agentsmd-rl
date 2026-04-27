"""Behavioral checks for openhands-infra-docsclaude-enforce-worktree-usage-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openhands-infra")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Common violation**: Skipping skill invocation and jumping straight to coding. This causes missed steps (reviewer bot iteration, PR templates, E2E test selection). The skill is not optional guidance ' in text, "expected to find: " + '**Common violation**: Skipping skill invocation and jumping straight to coding. This causes missed steps (reviewer bot iteration, PR templates, E2E test selection). The skill is not optional guidance '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Common violation**: Using `git checkout -b` on the main working tree. This pollutes the workspace and risks uncommitted changes interfering with the feature branch.' in text, "expected to find: " + '**Common violation**: Using `git checkout -b` on the main working tree. This pollutes the workspace and risks uncommitted changes interfering with the feature branch.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CRITICAL**: All feature development, bug fixes, and dependency updates MUST strictly follow the `github-workflow` skill.' in text, "expected to find: " + '**CRITICAL**: All feature development, bug fixes, and dependency updates MUST strictly follow the `github-workflow` skill.'[:80]

