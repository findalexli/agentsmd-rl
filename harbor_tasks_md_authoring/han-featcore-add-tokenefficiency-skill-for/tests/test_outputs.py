"""Behavioral checks for han-featcore-add-tokenefficiency-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/han")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/token-efficiency/SKILL.md')
    assert 'Minimize token consumption without sacrificing quality. Every token spent on overhead is a token not available for thinking.' in text, "expected to find: " + 'Minimize token consumption without sacrificing quality. Every token spent on overhead is a token not available for thinking.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/token-efficiency/SKILL.md')
    assert 'Always. Token efficiency is not premature optimization — it directly extends how much work fits in a session.' in text, "expected to find: " + 'Always. Token efficiency is not premature optimization — it directly extends how much work fits in a session.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/core/skills/token-efficiency/SKILL.md')
    assert '- **Use Edit for modifications** — sends only the diff (~50-100 tokens), not the whole file' in text, "expected to find: " + '- **Use Edit for modifications** — sends only the diff (~50-100 tokens), not the whole file'[:80]

