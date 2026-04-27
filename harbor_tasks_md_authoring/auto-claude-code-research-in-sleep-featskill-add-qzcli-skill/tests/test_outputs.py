"""Behavioral checks for auto-claude-code-research-in-sleep-featskill-add-qzcli-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qzcli/SKILL.md')
    assert 'description: Manage GPU compute jobs on the Qizhi (启智) platform using qzcli — a kubectl-style CLI tool. Use when user says "qzcli", "启智平台", "submit job", "stop job", "查计算组", "avail", "list jobs", "bat' in text, "expected to find: " + 'description: Manage GPU compute jobs on the Qizhi (启智) platform using qzcli — a kubectl-style CLI tool. Use when user says "qzcli", "启智平台", "submit job", "stop job", "查计算组", "avail", "list jobs", "bat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qzcli/SKILL.md')
    assert 'The TUI shows GPU type, availability, and spec status at each level. Press `Enter/→` to go deeper, `←` to go back.' in text, "expected to find: " + 'The TUI shows GPU type, availability, and spec status at each level. Press `Enter/→` to go deeper, `←` to go back.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qzcli/SKILL.md')
    assert '`CLI args > --password-stdin > env vars > QZCLI_ENV_FILE (.env) > ~/.qzcli/config.json > interactive input`' in text, "expected to find: " + '`CLI args > --password-stdin > env vars > QZCLI_ENV_FILE (.env) > ~/.qzcli/config.json > interactive input`'[:80]

