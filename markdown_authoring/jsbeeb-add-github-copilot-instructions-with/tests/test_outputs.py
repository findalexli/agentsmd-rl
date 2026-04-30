"""Behavioral checks for jsbeeb-add-github-copilot-instructions-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jsbeeb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'jsbeeb is a JavaScript BBC Micro emulator that runs in modern browsers and as an Electron desktop application. It emulates a 32K BBC B (with sideways RAM) and a 128K BBC Master, along with numerous pe' in text, "expected to find: " + 'jsbeeb is a JavaScript BBC Micro emulator that runs in modern browsers and as an Electron desktop application. It emulates a 32K BBC B (with sideways RAM) and a 128K BBC Master, along with numerous pe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '3. **Verify emulator loads**: Should see "Loading OS from roms/os.rom", "Loading ROM from roms/BASIC.ROM", "Loading ROM from roms/b/DFS-1.2.rom", "Loading disc from discs/elite.ssd" in console' in text, "expected to find: " + '3. **Verify emulator loads**: Should see "Loading OS from roms/os.rom", "Loading ROM from roms/BASIC.ROM", "Loading ROM from roms/b/DFS-1.2.rom", "Loading disc from discs/elite.ssd" in console'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.' in text, "expected to find: " + 'Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.'[:80]

