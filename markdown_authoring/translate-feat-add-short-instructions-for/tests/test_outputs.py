"""Behavioral checks for translate-feat-add-short-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/translate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use dependency groups for different environments (dev, test, docs, etc.)' in text, "expected to find: " + '- Use dependency groups for different environments (dev, test, docs, etc.)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Follow existing contributor documentation in `docs/developers/`.' in text, "expected to find: " + 'Follow existing contributor documentation in `docs/developers/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Pre-commit hooks are configured (`.pre-commit-config.yaml`)' in text, "expected to find: " + '- Pre-commit hooks are configured (`.pre-commit-config.yaml`)'[:80]

