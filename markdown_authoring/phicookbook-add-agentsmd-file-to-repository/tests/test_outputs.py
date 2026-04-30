"""Behavioral checks for phicookbook-add-agentsmd-file-to-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phicookbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "PhiCookBook is a comprehensive cookbook repository containing hands-on examples, tutorials, and documentation for working with Microsoft's Phi family of Small Language Models (SLMs). The repository de" in text, "expected to find: " + "PhiCookBook is a comprehensive cookbook repository containing hands-on examples, tutorials, and documentation for working with Microsoft's Phi family of Small Language Models (SLMs). The repository de"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains example code and tutorials rather than a traditional software project with unit tests. Validation is typically done by:' in text, "expected to find: " + 'This repository contains example code and tutorials rather than a traditional software project with unit tests. Validation is typically done by:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **02.Application/** - Application samples organized by type (Text, Code, Vision, Audio, etc.)' in text, "expected to find: " + '- **02.Application/** - Application samples organized by type (Text, Code, Vision, Audio, etc.)'[:80]

