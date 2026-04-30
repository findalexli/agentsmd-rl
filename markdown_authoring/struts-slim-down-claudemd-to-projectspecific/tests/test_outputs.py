"""Behavioral checks for struts-slim-down-claudemd-to-projectspecific (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/struts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- OGNL expressions have strict security via `SecurityMemberAccess` — test any new OGNL usage against the security sandbox.' in text, "expected to find: " + '- OGNL expressions have strict security via `SecurityMemberAccess` — test any new OGNL usage against the security sandbox.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Each plugin has its own `struts-plugin.xml` descriptor — register new beans there, not in core config.' in text, "expected to find: " + '- Each plugin has its own `struts-plugin.xml` descriptor — register new beans there, not in core config.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Uses **javax.servlet** (Java EE), not Jakarta EE. Verify imports use `javax.servlet` namespace.' in text, "expected to find: " + '- Uses **javax.servlet** (Java EE), not Jakarta EE. Verify imports use `javax.servlet` namespace.'[:80]

