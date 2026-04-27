"""Behavioral checks for loop-update-agentsmd-with-test-command (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/loop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Plain-text prompts auto-create `PLAN.md` first, then optionally run `--review-plan`; if you are changing planning behavior, keep that flow aligned.' in text, "expected to find: " + '- Plain-text prompts auto-create `PLAN.md` first, then optionally run `--review-plan`; if you are changing planning behavior, keep that flow aligned.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Running `loop` with no args opens the live panel for active sessions; keep panel-only changes separate from task-running changes when possible.' in text, "expected to find: " + '- Running `loop` with no args opens the live panel for active sessions; keep panel-only changes separate from task-running changes when possible.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `loop update` / `loop upgrade` are supported manual update commands for installed binaries; source runs should continue to rely on `git pull`.' in text, "expected to find: " + '- `loop update` / `loop upgrade` are supported manual update commands for installed binaries; source runs should continue to rely on `git pull`.'[:80]

