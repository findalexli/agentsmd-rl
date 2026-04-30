"""Behavioral checks for skills-feat-add-agentsmd-with-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'When changing the path to any Langfuse skill in this repo, you must also update the corresponding path reference in the [CLI repo](https://github.com/langfuse/langfuse-cli) so that it points to the ne' in text, "expected to find: " + 'When changing the path to any Langfuse skill in this repo, you must also update the corresponding path reference in the [CLI repo](https://github.com/langfuse/langfuse-cli) so that it points to the ne'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '## Langfuse Skill Path Changes' in text, "expected to find: " + '## Langfuse Skill Path Changes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '# Agent Instructions' in text, "expected to find: " + '# Agent Instructions'[:80]

