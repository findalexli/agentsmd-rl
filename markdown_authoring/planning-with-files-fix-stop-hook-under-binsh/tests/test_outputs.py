"""Behavioral checks for planning-with-files-fix-stop-hook-under-binsh (markdown_authoring task).

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
    text = _read('.codex/skills/planning-with-files/SKILL.md')
    assert 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/planning-with-files/SKILL.md')
    assert 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/planning-with-files/SKILL.md')
    assert 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"' in text, "expected to find: " + 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/planning-with-files/SKILL.md')
    assert 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/planning-with-files/SKILL.md')
    assert 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/skills/planning-with-files/SKILL.md')
    assert 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"' in text, "expected to find: " + 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.kilocode/skills/planning-with-files/SKILL.md')
    assert 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.kilocode/skills/planning-with-files/SKILL.md')
    assert 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.kilocode/skills/planning-with-files/SKILL.md')
    assert 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"' in text, "expected to find: " + 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/planning-with-files/SKILL.md')
    assert 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/planning-with-files/SKILL.md')
    assert 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/planning-with-files/SKILL.md')
    assert 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"' in text, "expected to find: " + 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'powershell -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||' in text, "expected to find: " + 'pwsh -ExecutionPolicy Bypass -File "$SCRIPT_DIR/check-complete.ps1" 2>/dev/null ||'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"' in text, "expected to find: " + 'UNAME_S="$(uname -s 2>/dev/null || echo \'\')"'[:80]

