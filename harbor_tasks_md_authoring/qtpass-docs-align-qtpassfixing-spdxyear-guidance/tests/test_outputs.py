"""Behavioral checks for qtpass-docs-align-qtpassfixing-spdxyear-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert 'Use the actual year the file was created — never a placeholder, never a year range. Repository convention is a single literal year (the existing files are 2014/2015/2016/2018/2020/2026, all real years' in text, "expected to find: " + 'Use the actual year the file was created — never a placeholder, never a year range. Repository convention is a single literal year (the existing files are 2014/2015/2016/2018/2020/2026, all real years'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert '// Bad — placeholder; reviewers will ask for a real year' in text, "expected to find: " + '// Bad — placeholder; reviewers will ask for a real year'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/qtpass-fixing/SKILL.md')
    assert '// SPDX-FileCopyrightText: 2014-2026 Your Name' in text, "expected to find: " + '// SPDX-FileCopyrightText: 2014-2026 Your Name'[:80]

