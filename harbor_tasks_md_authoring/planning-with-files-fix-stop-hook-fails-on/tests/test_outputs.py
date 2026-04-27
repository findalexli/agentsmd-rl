"""Behavioral checks for planning-with-files-fix-stop-hook-fails-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/planning-with-files")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.codebuddy/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${CODEBUDDY_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$' in text, "expected to find: " + 'command: "SD=\\"${CODEBUDDY_PLUGIN_ROOT:-$HOME/.codebuddy/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${CODEX_SKILL_ROOT:-$HOME/.codex/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/check-' in text, "expected to find: " + 'command: "SD=\\"${CODEX_SKILL_ROOT:-$HOME/.codex/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/check-'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${CURSOR_SKILL_ROOT:-.cursor/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/check-comp' in text, "expected to find: " + 'command: "SD=\\"${CURSOR_SKILL_ROOT:-.cursor/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/check-comp'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.kilocode/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${KILOCODE_SKILL_ROOT:-$HOME/.kilocode/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/' in text, "expected to find: " + 'command: "SD=\\"${KILOCODE_SKILL_ROOT:-$HOME/.kilocode/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.mastracode/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"$HOME/.mastracode/skills/planning-with-files/scripts\\"; [ -f \\"$SD/check-complete.sh\\" ] || SD=\\".mastracode/skills/planning-with-files/scripts\\"; powershell.exe -NoProfile -ExecutionPo' in text, "expected to find: " + 'command: "SD=\\"$HOME/.mastracode/skills/planning-with-files/scripts\\"; [ -f \\"$SD/check-complete.sh\\" ] || SD=\\".mastracode/skills/planning-with-files/scripts\\"; powershell.exe -NoProfile -ExecutionPo'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${OPENCODE_SKILL_ROOT:-$HOME/.config/opencode/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh' in text, "expected to find: " + 'command: "SD=\\"${OPENCODE_SKILL_ROOT:-$HOME/.config/opencode/skills/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'command: "SD=\\"${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/ch' in text, "expected to find: " + 'command: "SD=\\"${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/planning-with-files}/scripts\\"; powershell.exe -NoProfile -ExecutionPolicy Bypass -File \\"$SD/check-complete.ps1\\" 2>/dev/null || sh \\"$SD/ch'[:80]

