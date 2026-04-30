"""Behavioral checks for cloudbase-mcp-featauthweb-wire-sdk-calls-into (markdown_authoring task).

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
    assert 'When the project already has `handleSendCode` / `handleRegister` or similar UI handlers, wire the SDK calls there directly instead of leaving them commented out in `App.tsx`.' in text, "expected to find: " + 'When the project already has `handleSendCode` / `handleRegister` or similar UI handlers, wire the SDK calls there directly instead of leaving them commented out in `App.tsx`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/auth-web/SKILL.md')
    assert '- Creating a detached helper file with `auth.signUp` / `verifyOtp` but never wiring it into the existing form handlers, so the actual button clicks still do nothing.' in text, "expected to find: " + '- Creating a detached helper file with `auth.signUp` / `verifyOtp` but never wiring it into the existing form handlers, so the actual button clicks still do nothing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/source/skills/auth-web/SKILL.md')
    assert "if (!signUpData?.verifyOtp) throw new Error('Please send the code first')" in text, "expected to find: " + "if (!signUpData?.verifyOtp) throw new Error('Please send the code first')"[:80]

