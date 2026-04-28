"""Behavioral checks for grida-docsskills-add-naming-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/grida")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/SKILL.md')
    assert 'central discipline is that a strict, honest name refuses to grow, and that' in text, "expected to find: " + 'central discipline is that a strict, honest name refuses to grow, and that'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/SKILL.md')
    assert 'How to think about names in the Grida repo — not conventions, but what a' in text, "expected to find: " + 'How to think about names in the Grida repo — not conventions, but what a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/SKILL.md')
    assert 'name commits you to, reveals about the system, and costs to change. The' in text, "expected to find: " + 'name commits you to, reveals about the system, and costs to change. The'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/cases.md')
    assert '| Directory                   | `name`              | Rationale                                         |' in text, "expected to find: " + '| Directory                   | `name`              | Rationale                                         |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/cases.md')
    assert '| `crates/grida-canvas`       | `cg`                | Heavily imported; short name pays off everywhere. |' in text, "expected to find: " + '| `crates/grida-canvas`       | `cg`                | Heavily imported; short name pays off everywhere. |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/naming/cases.md')
    assert '| `crates/grida-canvas-fonts` | `fonts`             | Scoped under `grida-canvas`; `fonts` is clear.    |' in text, "expected to find: " + '| `crates/grida-canvas-fonts` | `fonts`             | Scoped under `grida-canvas`; `fonts` is clear.    |'[:80]

