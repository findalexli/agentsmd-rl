"""Behavioral checks for agent-skills-cloud-remote-access-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('laravel-cloud/skills/deploying-laravel-cloud/SKILL.md')
    assert 'The code must explicitly output results using `echo`, `dump`, or similar — expressions alone produce no output.' in text, "expected to find: " + 'The code must explicitly output results using `echo`, `dump`, or similar — expressions alone produce no output.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('laravel-cloud/skills/deploying-laravel-cloud/SKILL.md')
    assert '- `cloud command:get {commandId} --json -n` — get details and output of a specific command' in text, "expected to find: " + '- `cloud command:get {commandId} --json -n` — get details and output of a specific command'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('laravel-cloud/skills/deploying-laravel-cloud/SKILL.md')
    assert "cloud tinker {environment} --code='Your PHP code here' --timeout=60 -n" in text, "expected to find: " + "cloud tinker {environment} --code='Your PHP code here' --timeout=60 -n"[:80]

