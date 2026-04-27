"""Behavioral checks for antigravity-awesome-skills-add-windowsshellreliability-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/windows-shell-reliability/SKILL.md')
    assert "| Background | `Start-Process dotnet -ArgumentList 'run' -RedirectStandardOutput output.txt -RedirectStandardError error.txt` | Launches the app without blocking the shell and keeps logs. |" in text, "expected to find: " + "| Background | `Start-Process dotnet -ArgumentList 'run' -RedirectStandardOutput output.txt -RedirectStandardError error.txt` | Launches the app without blocking the shell and keeps logs. |"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/windows-shell-reliability/SKILL.md')
    assert 'Use this skill when developing or debugging scripts and automation that run on Windows systems, especially when involving file paths, character encoding, or standard CLI tools.' in text, "expected to find: " + 'Use this skill when developing or debugging scripts and automation that run on Windows systems, especially when involving file paths, character encoding, or standard CLI tools.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/windows-shell-reliability/SKILL.md')
    assert '| `Encoding mismatch` | Older shell redirection rewrote the output | Re-export the file as UTF-8 or capture with `2>&1 | Out-File -Encoding UTF8`. |' in text, "expected to find: " + '| `Encoding mismatch` | Older shell redirection rewrote the output | Re-export the file as UTF-8 or capture with `2>&1 | Out-File -Encoding UTF8`. |'[:80]

