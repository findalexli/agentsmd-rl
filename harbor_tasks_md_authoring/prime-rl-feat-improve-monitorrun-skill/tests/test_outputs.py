"""Behavioral checks for prime-rl-feat-improve-monitorrun-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prime-rl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert 'The output directory and tmux session name are typically provided by the researcher in the appended system prompt (see `scripts/tmux.sh` — the Claude window is launched with this context). If not prov' in text, "expected to find: " + 'The output directory and tmux session name are typically provided by the researcher in the appended system prompt (see `scripts/tmux.sh` — the Claude window is launched with this context). If not prov'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert '**IMPORTANT**: Never restart a run unless you were explicitly instructed by the researcher. If you were given permission, make sure to ask the researcher for the exact command to resume a run and unde' in text, "expected to find: " + '**IMPORTANT**: Never restart a run unless you were explicitly instructed by the researcher. If you were given permission, make sure to ask the researcher for the exact command to resume a run and unde'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert 'As part of every check-in, grep all logs for `WARNING` and `ERROR` level messages. Pay special attention to env server and env worker logs — these are the most common source of issues since they run u' in text, "expected to find: " + 'As part of every check-in, grep all logs for `WARNING` and `ERROR` level messages. Pay special attention to env server and env worker logs — these are the most common source of issues since they run u'[:80]

