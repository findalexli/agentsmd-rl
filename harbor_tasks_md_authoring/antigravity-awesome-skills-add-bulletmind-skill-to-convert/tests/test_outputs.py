"""Behavioral checks for antigravity-awesome-skills-add-bulletmind-skill-to-convert (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/EXAMPLES.md')
    assert '- Software that manages computer hardware and software resources and provides a platform and interface for applications to run.' in text, "expected to find: " + '- Software that manages computer hardware and software resources and provides a platform and interface for applications to run.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/EXAMPLES.md')
    assert '- Long-term shift in global temperatures and weather patterns' in text, "expected to find: " + '- Long-term shift in global temperatures and weather patterns'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/EXAMPLES.md')
    assert '- Controls and coordinates hardware components' in text, "expected to find: " + '- Controls and coordinates hardware components'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/SKILL.md')
    assert 'When active, responses remain in hierarchical bullet format with no paragraphs, no prose blocks, no drift, and only structured bullet output.' in text, "expected to find: " + 'When active, responses remain in hierarchical bullet format with no paragraphs, no prose blocks, no drift, and only structured bullet output.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/SKILL.md')
    assert 'description: "Convert input into clean, structured, hierarchical bullet points for summarization, note-taking, and structured thinking."' in text, "expected to find: " + 'description: "Convert input into clean, structured, hierarchical bullet points for summarization, note-taking, and structured thinking."'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bulletmind/SKILL.md')
    assert '- Do not preserve bullet-only formatting if a higher-priority instruction requires tables, code blocks, JSON, or paragraphs.' in text, "expected to find: " + '- Do not preserve bullet-only formatting if a higher-priority instruction requires tables, code blocks, JSON, or paragraphs.'[:80]

