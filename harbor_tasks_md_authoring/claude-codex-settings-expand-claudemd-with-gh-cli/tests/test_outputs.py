"""Behavioral checks for claude-codex-settings-expand-claudemd-with-gh-cli (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-codex-settings")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Before exiting the plan mode**: Never assume anything. Always run tests with `python -c "..."` to verify you hypothesis and bugfix candidates about code behavior, package functions, or data struct' in text, "expected to find: " + '- **Before exiting the plan mode**: Never assume anything. Always run tests with `python -c "..."` to verify you hypothesis and bugfix candidates about code behavior, package functions, or data struct'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '4. **Cited Claims**: Every specific claim attributed to a paper (e.g., "9% improvement on Synthia", "4.7% on OpenImages") must be verifiable in the actual paper text. If a number cannot be confirmed, ' in text, "expected to find: " + '4. **Cited Claims**: Every specific claim attributed to a paper (e.g., "9% improvement on Synthia", "4.7% on OpenImages") must be verifiable in the actual paper text. If a number cannot be confirmed, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- After adding citations into md or bibtex entries into biblo.bib, fact check all fields from web. Even if you performed fact check before, always do it again after writing the citation in the documen' in text, "expected to find: " + '- After adding citations into md or bibtex entries into biblo.bib, fact check all fields from web. Even if you performed fact check before, always do it again after writing the citation in the documen'[:80]

