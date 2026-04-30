"""Behavioral checks for cloudbase-mcp-fixskill-add-signinwithpassword-return-format (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cloudbase-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/auth-web/SKILL.md')
    assert "const { data, error } = await auth.signInWithPassword({ username: 'test_user', password: 'pass123' })" in text, "expected to find: " + "const { data, error } = await auth.signInWithPassword({ username: 'test_user', password: 'pass123' })"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/auth-web/SKILL.md')
    assert "// await auth.signInWithPassword({ email: 'user@example.com', password: 'pass123' })" in text, "expected to find: " + "// await auth.signInWithPassword({ email: 'user@example.com', password: 'pass123' })"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/auth-web/SKILL.md')
    assert "// await auth.signInWithPassword({ phone: '13800138000', password: 'pass123' })" in text, "expected to find: " + "// await auth.signInWithPassword({ phone: '13800138000', password: 'pass123' })"[:80]

