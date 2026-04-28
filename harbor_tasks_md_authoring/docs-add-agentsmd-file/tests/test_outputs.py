"""Behavioral checks for docs-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/current/AGENTS.md')
    assert 'Note: The Liquid variable `{{page.version.version}}` resolves to the major version in the path of the page where it is used (e.g. `v25.4`). References to version-specific includes often use this, allo' in text, "expected to find: " + 'Note: The Liquid variable `{{page.version.version}}` resolves to the major version in the path of the page where it is used (e.g. `v25.4`). References to version-specific includes often use this, allo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/current/AGENTS.md')
    assert "Hello! We're working together on docs for CockroachDB, a distributed SQL database. The docs are located in Markdown files (with Liquid templates) in various subdirectories of this one." in text, "expected to find: " + "Hello! We're working together on docs for CockroachDB, a distributed SQL database. The docs are located in Markdown files (with Liquid templates) in various subdirectories of this one."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/current/AGENTS.md')
    assert 'For includes that we can assume only apply to specific versions, though in some cases, their content may be identical across all versions where the file exists:' in text, "expected to find: " + 'For includes that we can assume only apply to specific versions, though in some cases, their content may be identical across all versions where the file exists:'[:80]

