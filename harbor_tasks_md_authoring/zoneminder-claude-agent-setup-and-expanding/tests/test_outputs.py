"""Behavioral checks for zoneminder-claude-agent-setup-and-expanding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zoneminder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'ZoneMinder is an integrated Linux-based CCTV surveillance system that provides capture, analysis, recording, and monitoring of video cameras. It consists of:' in text, "expected to find: " + 'ZoneMinder is an integrated Linux-based CCTV surveillance system that provides capture, analysis, recording, and monitoring of video cameras. It consists of:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Understanding GitHub and Pull Requests](https://github.com/ZoneMinder/ZoneMinder/wiki/Understanding-Github-and-Pull-Requests)' in text, "expected to find: " + '- [Understanding GitHub and Pull Requests](https://github.com/ZoneMinder/ZoneMinder/wiki/Understanding-Github-and-Pull-Requests)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Feature Workflow**: GitHub Issue → Feature Branch → Implement FULLY → Tests Pass → Get Approval → Merge to master' in text, "expected to find: " + '3. **Feature Workflow**: GitHub Issue → Feature Branch → Implement FULLY → Tests Pass → Get Approval → Merge to master'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

