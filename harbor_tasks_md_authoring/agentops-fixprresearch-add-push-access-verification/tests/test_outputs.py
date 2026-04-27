"""Behavioral checks for agentops-fixprresearch-add-push-access-verification (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/pr-kit/skills/pr-research/SKILL.md')
    assert '**Unless `viewerPermission` is `ADMIN` or `WRITE`, assume fork-based workflow is required.**' in text, "expected to find: " + '**Unless `viewerPermission` is `ADMIN` or `WRITE`, assume fork-based workflow is required.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/pr-kit/skills/pr-research/SKILL.md')
    assert '| **Assume push access** | **Always verify with `gh repo view --json viewerPermission`** |' in text, "expected to find: " + '| **Assume push access** | **Always verify with `gh repo view --json viewerPermission`** |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/pr-kit/skills/pr-research/SKILL.md')
    assert '**CRITICAL**: Never assume the user has push access to external repositories.' in text, "expected to find: " + '**CRITICAL**: Never assume the user has push access to external repositories.'[:80]

