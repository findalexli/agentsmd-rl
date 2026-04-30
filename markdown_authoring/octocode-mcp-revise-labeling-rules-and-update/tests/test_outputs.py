"""Behavioral checks for octocode-mcp-revise-labeling-rules-and-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/octocode-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-pull-request-reviewer/SKILL.md')
    assert '- **FORBIDDEN:** Using `#1`, `#2`, or any `#<number>` notation to label or reference findings anywhere in the output. GitHub auto-links `#N` to issues and pull requests, creating broken or misleading ' in text, "expected to find: " + '- **FORBIDDEN:** Using `#1`, `#2`, or any `#<number>` notation to label or reference findings anywhere in the output. GitHub auto-links `#N` to issues and pull requests, creating broken or misleading '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-pull-request-reviewer/SKILL.md')
    assert '- **FORBIDDEN:** Using `#1`, `#2`, `#N` or any `#<number>` prefix to label findings or reference them in text. GitHub auto-links `#<number>` as issue/PR references, creating broken or misleading cross' in text, "expected to find: " + '- **FORBIDDEN:** Using `#1`, `#2`, `#N` or any `#<number>` prefix to label findings or reference them in text. GitHub auto-links `#<number>` as issue/PR references, creating broken or misleading cross'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/octocode-pull-request-reviewer/SKILL.md')
    assert '- Use plain numbering (`1.`, `2.`), lettered labels (`A`, `B`), or descriptive category IDs (e.g., `[SEC-1]`, `[BUG-1]`, `[ARCH-1]`) instead.' in text, "expected to find: " + '- Use plain numbering (`1.`, `2.`), lettered labels (`A`, `B`), or descriptive category IDs (e.g., `[SEC-1]`, `[BUG-1]`, `[ARCH-1]`) instead.'[:80]

