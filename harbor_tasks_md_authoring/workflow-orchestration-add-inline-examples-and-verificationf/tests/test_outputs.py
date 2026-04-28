"""Behavioral checks for workflow-orchestration-add-inline-examples-and-verificationf (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workflow-orchestration")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'prompt: "Find all authentication middleware in src/ and list file paths with a one-line summary of each."' in text, "expected to find: " + 'prompt: "Find all authentication middleware in src/ and list file paths with a one-line summary of each."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Inline example** (full templates in [references/task-templates.md](references/task-templates.md)):' in text, "expected to find: " + '**Inline example** (full templates in [references/task-templates.md](references/task-templates.md)):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**Inline example** (full template in [references/lessons-format.md](references/lessons-format.md)):' in text, "expected to find: " + '**Inline example** (full template in [references/lessons-format.md](references/lessons-format.md)):'[:80]

