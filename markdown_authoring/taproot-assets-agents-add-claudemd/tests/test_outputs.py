"""Behavioral checks for taproot-assets-agents-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/taproot-assets")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Integration tests (`itest/`) run full tapd instances with btcd and lnd. Test cases are registered in `itest/test_list_on_test.go`.' in text, "expected to find: " + 'Integration tests (`itest/`) run full tapd instances with btcd and lnd. Test cases are registered in `itest/test_list_on_test.go`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Run specific integration test (test names from itest/test_list_on_test.go, snake_cased)' in text, "expected to find: " + '# Run specific integration test (test names from itest/test_list_on_test.go, snake_cased)'[:80]

