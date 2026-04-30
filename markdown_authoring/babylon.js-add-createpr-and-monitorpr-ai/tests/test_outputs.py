"""Behavioral checks for babylon.js-add-createpr-and-monitorpr-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/babylon.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/create-pr/SKILL.md')
    assert 'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'Fixes are staged and ready for review.\', \'Fixes Ready\', \'OK\', \'Information\')"' in text, "expected to find: " + 'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'Fixes are staged and ready for review.\', \'Fixes Ready\', \'OK\', \'Information\')"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/create-pr/SKILL.md')
    assert '| Argument                   | Description                                                                                                                 |' in text, "expected to find: " + '| Argument                   | Description                                                                                                                 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/create-pr/SKILL.md')
    assert "| `--push-remote <fork>`     | Git remote (user's fork) to push the branch to. If omitted, detect and prompt.                                              |" in text, "expected to find: " + "| `--push-remote <fork>`     | Git remote (user's fork) to push the branch to. If omitted, detect and prompt.                                              |"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/monitor-pr/SKILL.md')
    assert 'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'PR #<number> — <title> — is ready to merge.\', \'PR Ready\', \'OK\', \'Information\')"' in text, "expected to find: " + 'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'PR #<number> — <title> — is ready to merge.\', \'PR Ready\', \'OK\', \'Information\')"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/monitor-pr/SKILL.md')
    assert '| Column   | Source                                                                                                                                     |' in text, "expected to find: " + '| Column   | Source                                                                                                                                     |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/monitor-pr/SKILL.md')
    assert '| PR       | `#<number>` linked to the PR URL                                                                                                           |' in text, "expected to find: " + '| PR       | `#<number>` linked to the PR URL                                                                                                           |'[:80]

