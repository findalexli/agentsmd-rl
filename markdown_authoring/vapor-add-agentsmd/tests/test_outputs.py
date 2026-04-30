"""Behavioral checks for vapor-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vapor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Security vulnerabilities must be reported by humans through our responsible disclosure process. Automated scanning tools may identify potential issues, but all security reports must be reviewed, verif' in text, "expected to find: " + 'Security vulnerabilities must be reported by humans through our responsible disclosure process. Automated scanning tools may identify potential issues, but all security reports must be reviewed, verif'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Issues tagged with `good-first-issue` are there to allow new contributors to learn the processs of contributing to open source and Vapor with relatively easy tasks, to help grow open source. These iss' in text, "expected to find: " + 'Issues tagged with `good-first-issue` are there to allow new contributors to learn the processs of contributing to open source and Vapor with relatively easy tasks, to help grow open source. These iss'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Open source thrives on human collaboration. Automated noise—whether from bots filing low-quality issues or agents submitting unreviewed code—drains maintainer energy and undermines the community we ar' in text, "expected to find: " + 'Open source thrives on human collaboration. Automated noise—whether from bots filing low-quality issues or agents submitting unreviewed code—drains maintainer energy and undermines the community we ar'[:80]

