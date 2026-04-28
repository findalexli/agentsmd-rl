"""Behavioral checks for navigator-update-navloop-skillmd-with-v2 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/navigator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nav-loop/SKILL.md')
    assert 'The JSON format in a `pilot-signal` code block ensures unambiguous detection by Pilot automation. The `reason` field should briefly describe why the task is complete.' in text, "expected to find: " + 'The JSON format in a `pilot-signal` code block ensures unambiguous detection by Pilot automation. The `reason` field should briefly describe why the task is complete.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nav-loop/SKILL.md')
    assert '{"v":2,"type":"exit","success":true,"reason":"isPrime function implemented and tests passing"}' in text, "expected to find: " + '{"v":2,"type":"exit","success":true,"reason":"isPrime function implemented and tests passing"}'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/nav-loop/SKILL.md')
    assert '**When exit conditions met**, emit the exit signal in JSON format and display completion:' in text, "expected to find: " + '**When exit conditions met**, emit the exit signal in JSON format and display completion:'[:80]

