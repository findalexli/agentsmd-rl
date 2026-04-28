"""Behavioral checks for hail-docs-repospecific-claude-skills-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hail")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch-dev.md')
    assert "If you hit a gap in the CLI during an investigation (e.g. there's no `hailctl batch jobs BATCH_ID` to list jobs within a batch — you currently need the Python client or `hailctl curl` for that), it ma" in text, "expected to find: " + "If you hit a gap in the CLI during an investigation (e.g. there's no `hailctl batch jobs BATCH_ID` to list jobs within a batch — you currently need the Python client or `hailctl curl` for that), it ma"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch-dev.md')
    assert '**Important**: both commands affect live infrastructure. Do not run them without explicit confirmation from the user — either ask the user to run the command themselves, or show the exact command and ' in text, "expected to find: " + '**Important**: both commands affect live infrastructure. Do not run them without explicit confirmation from the user — either ask the user to run the command themselves, or show the exact command and '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch-dev.md')
    assert "Then ask whether they'd like you to watch it too and verify the deployment looks good when it comes up (useful if they want to iterate on failures). Waiting can take 20-30 minutes, so only do it if th" in text, "expected to find: " + "Then ask whether they'd like you to watch it too and verify the deployment looks good when it comes up (useful if they want to iterate on failures). Waiting can take 20-30 minutes, so only do it if th"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch.md')
    assert "For inspection tasks (checking status, reading logs, diagnosing failures), **always prefer `hailctl batch` CLI commands** — they're simpler and don't require writing Python." in text, "expected to find: " + "For inspection tasks (checking status, reading logs, diagnosing failures), **always prefer `hailctl batch` CLI commands** — they're simpler and don't require writing Python."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch.md')
    assert '**Never suppress stderr** when running hailctl or other Hail tools — important connection info and warnings appear there. Do not use `2>&1` or `2>/dev/null`.' in text, "expected to find: " + '**Never suppress stderr** when running hailctl or other Hail tools — important connection info and warnings appear there. Do not use `2>&1` or `2>/dev/null`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/hail-batch.md')
    assert "If `hailctl` isn't found, it may be in a virtual environment — look for one and activate it. Once activated, it stays active for the session." in text, "expected to find: " + "If `hailctl` isn't found, it may be in a virtual environment — look for one and activate it. Once activated, it stays active for the session."[:80]

