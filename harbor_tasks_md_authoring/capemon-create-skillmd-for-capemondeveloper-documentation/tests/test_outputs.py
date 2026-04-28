"""Behavioral checks for capemon-create-skillmd-for-capemondeveloper-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/capemon")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.gemini/skills/capemon-developer/SKILL.md')
    assert 'description: Expert capability for navigating, modifying, and extending the capemon malware monitoring codebase. Includes deep knowledge of Windows API hooking, PE structures, and the CAPEv2 sandbox a' in text, "expected to find: " + 'description: Expert capability for navigating, modifying, and extending the capemon malware monitoring codebase. Includes deep knowledge of Windows API hooking, PE structures, and the CAPEv2 sandbox a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.gemini/skills/capemon-developer/SKILL.md')
    assert '`capemon` is a sophisticated monitoring and instrumentation engine designed for malware analysis, configuration extraction, and payload recovery. It acts as the core injection component for the CAPEv2' in text, "expected to find: " + '`capemon` is a sophisticated monitoring and instrumentation engine designed for malware analysis, configuration extraction, and payload recovery. It acts as the core injection component for the CAPEv2'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.gemini/skills/capemon-developer/SKILL.md')
    assert '- **Stealth:** Debugger does not rely upon Windows interface and thus evades detection by a slew of interface-related indicators, with additional stealth from hook-based protections' in text, "expected to find: " + '- **Stealth:** Debugger does not rely upon Windows interface and thus evades detection by a slew of interface-related indicators, with additional stealth from hook-based protections'[:80]

