"""Behavioral checks for redb-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "[Linux Kernel's coding assistant guidelines](https://github.com/torvalds/linux/blob/master/Documentation/process/coding-assistants.rst)." in text, "expected to find: " + "[Linux Kernel's coding assistant guidelines](https://github.com/torvalds/linux/blob/master/Documentation/process/coding-assistants.rst)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1) git commits should use your human\'s name and email address for authorship. Add "Assisted-by:" and' in text, "expected to find: " + '1) git commits should use your human\'s name and email address for authorship. Add "Assisted-by:" and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2) Make one commit per feature / bug fix when opening a PR. Multiple commits or "fixup" commits are' in text, "expected to find: " + '2) Make one commit per feature / bug fix when opening a PR. Multiple commits or "fixup" commits are'[:80]

