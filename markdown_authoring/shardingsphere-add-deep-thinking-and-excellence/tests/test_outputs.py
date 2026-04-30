"""Behavioral checks for shardingsphere-add-deep-thinking-and-excellence (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shardingsphere")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `Pluggable:` Leveraging micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO' in text, "expected to find: " + '- `Pluggable:` Leveraging micro kernel and 3 layers pluggable mode, features and database ecosystem can be embedded flexibly. Developers can customize their ShardingSphere just like building with LEGO'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multiple approaches, anticipate issues' in text, "expected to find: " + '- **Comprehensive Analysis**: Thoroughly analyze problem context, consider multiple approaches, anticipate issues'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Quality Validation**: Ensure immediate usability, actionable recommendations, alignment with best practices' in text, "expected to find: " + '- **Quality Validation**: Ensure immediate usability, actionable recommendations, alignment with best practices'[:80]

