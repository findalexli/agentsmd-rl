"""Behavioral checks for dash_skills-enhance-skillmd-with-windows-support (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dash-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-cli-app-best-practices/SKILL.md')
    assert 'When writing CLI applications and tests, ensure compatibility with Windows:' in text, "expected to find: " + 'When writing CLI applications and tests, ensure compatibility with Windows:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-cli-app-best-practices/SKILL.md')
    assert '`chmod` is not available on Windows. Use `icacls` on Windows or appropriate' in text, "expected to find: " + '`chmod` is not available on Windows. Use `icacls` on Windows or appropriate'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/dart-cli-app-best-practices/SKILL.md')
    assert "- **Paths**: Never hardcode path separators like `/`. Use `package:path`'s" in text, "expected to find: " + "- **Paths**: Never hardcode path separators like `/`. Use `package:path`'s"[:80]

