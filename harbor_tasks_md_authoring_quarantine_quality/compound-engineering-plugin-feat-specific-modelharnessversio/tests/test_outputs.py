"""Behavioral checks for compound-engineering-plugin-feat-specific-modelharnessversio (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]' in text, "expected to find: " + '🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Co-Authored-By: [MODEL] ([CONTEXT] context, [THINKING]) <noreply@anthropic.com>' in text, "expected to find: " + 'Co-Authored-By: [MODEL] ([CONTEXT] context, [THINKING]) <noreply@anthropic.com>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |' in text, "expected to find: " + '| `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)' in text, "expected to find: " + '[![Compound Engineering v[VERSION]](https://img.shields.io/badge/Compound_Engineering-v[VERSION]-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '- [ ] PR description includes Compound Engineered badge with accurate model, harness, and version' in text, "expected to find: " + '- [ ] PR description includes Compound Engineered badge with accurate model, harness, and version'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]' in text, "expected to find: " + '🤖 Generated with [MODEL] via [HARNESS](HARNESS_URL) + Compound Engineering v[VERSION]'[:80]

