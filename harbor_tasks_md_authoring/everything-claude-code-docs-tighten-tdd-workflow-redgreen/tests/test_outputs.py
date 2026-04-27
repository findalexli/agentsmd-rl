"""Behavioral checks for everything-claude-code-docs-tighten-tdd-workflow-redgreen (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tdd-workflow/SKILL.md')
    assert '- Before treating a checkpoint as satisfied, verify that the commit is reachable from the current `HEAD` on the active branch and belongs to the current task sequence' in text, "expected to find: " + '- Before treating a checkpoint as satisfied, verify that the commit is reachable from the current `HEAD` on the active branch and belongs to the current task sequence'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tdd-workflow/SKILL.md')
    assert '- Separate evidence-only commits are not required if the test commit clearly corresponds to RED and the fix commit clearly corresponds to GREEN' in text, "expected to find: " + '- Separate evidence-only commits are not required if the test commit clearly corresponds to RED and the fix commit clearly corresponds to GREEN'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tdd-workflow/SKILL.md')
    assert '- This commit may also serve as the RED validation checkpoint if the reproducer was compiled and executed and failed for the intended reason' in text, "expected to find: " + '- This commit may also serve as the RED validation checkpoint if the reproducer was compiled and executed and failed for the intended reason'[:80]

