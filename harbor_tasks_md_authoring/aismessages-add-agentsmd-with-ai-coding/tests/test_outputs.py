"""Behavioral checks for aismessages-add-agentsmd-with-ai-coding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aismessages")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository is a Java project built with Maven. When collaborating with any AI coding agent, follow these guidelines for effective results:' in text, "expected to find: " + 'This repository is a Java project built with Maven. When collaborating with any AI coding agent, follow these guidelines for effective results:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Key packages:** AIS message decoder in `dk.tbsalling.aismessages`; demos in `dk.tbsalling.aismessages.demo`' in text, "expected to find: " + '- **Key packages:** AIS message decoder in `dk.tbsalling.aismessages`; demos in `dk.tbsalling.aismessages.demo`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Standard Java conventions (4-space indent, meaningful names, prefer immutability)' in text, "expected to find: " + '- Standard Java conventions (4-space indent, meaningful names, prefer immutability)'[:80]

