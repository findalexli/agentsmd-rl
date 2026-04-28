"""Behavioral checks for prism-update-doc-paths-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prism")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/boost/skills/developing-with-prism/SKILL.md')
    assert 'read vendor/prism-php/prism/docs/core-concepts/text-generation.md' in text, "expected to find: " + 'read vendor/prism-php/prism/docs/core-concepts/text-generation.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/boost/skills/developing-with-prism/SKILL.md')
    assert 'grep "withProviderOptions" vendor/prism-php/prism/docs/providers/' in text, "expected to find: " + 'grep "withProviderOptions" vendor/prism-php/prism/docs/providers/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('resources/boost/skills/developing-with-prism/SKILL.md')
    assert 'read vendor/prism-php/prism/docs/providers/openai.md' in text, "expected to find: " + 'read vendor/prism-php/prism/docs/providers/openai.md'[:80]

