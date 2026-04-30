"""Behavioral checks for beads-update-references-to-workflowsmd-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/beads")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert '- **Compaction Strategies**: `{baseDir}/references/WORKFLOWS.md`' in text, "expected to find: " + '- **Compaction Strategies**: `{baseDir}/references/WORKFLOWS.md`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert '- **Epic Management**: `{baseDir}/references/WORKFLOWS.md`' in text, "expected to find: " + '- **Epic Management**: `{baseDir}/references/WORKFLOWS.md`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/beads/SKILL.md')
    assert '- **Template System**: `{baseDir}/references/WORKFLOWS.md`' in text, "expected to find: " + '- **Template System**: `{baseDir}/references/WORKFLOWS.md`'[:80]

