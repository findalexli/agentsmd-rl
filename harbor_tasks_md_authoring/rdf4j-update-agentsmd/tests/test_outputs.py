"""Behavioral checks for rdf4j-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rdf4j")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Exception: if no GitHub issue number is available for the task, clearly note this in your handoff and align with the requester on an appropriate branch/commit prefix before proceeding.' in text, "expected to find: " + '* Exception: if no GitHub issue number is available for the task, clearly note this in your handoff and align with the requester on an appropriate branch/commit prefix before proceeding.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Branch names must always start with the GitHub issue identifier in the form `GH-XXXX`, where `XXXX` is the numeric issue number.' in text, "expected to find: " + '* Branch names must always start with the GitHub issue identifier in the form `GH-XXXX`, where `XXXX` is the numeric issue number.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* Every commit message must be prefixed with the corresponding `GH-XXXX` label.' in text, "expected to find: " + '* Every commit message must be prefixed with the corresponding `GH-XXXX` label.'[:80]

