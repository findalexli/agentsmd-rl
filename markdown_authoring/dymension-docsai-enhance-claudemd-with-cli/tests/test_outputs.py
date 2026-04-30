"""Behavioral checks for dymension-docsai-enhance-claudemd-with-cli (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dymension")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The `dymd` command-line interface is the primary tool for interacting with the Dymension blockchain. It provides commands for node operations, key management, querying blockchain state, and broadcasti' in text, "expected to find: " + 'The `dymd` command-line interface is the primary tool for interacting with the Dymension blockchain. It provides commands for node operations, key management, querying blockchain state, and broadcasti'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Remember: These tools can take significant time to run, especially proto generation and full test suites.' in text, "expected to find: " + 'Remember: These tools can take significant time to run, especially proto generation and full test suites.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'dymd tx rollapp add-app rollapp_1234-1 "App Name" "Description" "https://app.url" --from owner' in text, "expected to find: " + 'dymd tx rollapp add-app rollapp_1234-1 "App Name" "Description" "https://app.url" --from owner'[:80]

