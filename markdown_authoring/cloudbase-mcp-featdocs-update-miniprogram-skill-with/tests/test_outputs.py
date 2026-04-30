"""Behavioral checks for cloudbase-mcp-featdocs-update-miniprogram-skill-with (markdown_authoring task).

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
    text = _read('config/.claude/skills/miniprogram-development/SKILL.md')
    assert "- When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)" in text, "expected to find: " + "- When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/miniprogram-development/SKILL.md')
    assert '- Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`' in text, "expected to find: " + '- Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.claude/skills/miniprogram-development/SKILL.md')
    assert '- Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`' in text, "expected to find: " + '- Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.codebuddy/skills/miniprogram-development/SKILL.md')
    assert "- When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)" in text, "expected to find: " + "- When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.codebuddy/skills/miniprogram-development/SKILL.md')
    assert '- Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`' in text, "expected to find: " + '- Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('config/.codebuddy/skills/miniprogram-development/SKILL.md')
    assert '- Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`' in text, "expected to find: " + '- Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`'[:80]

