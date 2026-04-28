"""Behavioral checks for stream-chat-js-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stream-chat-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Official JavaScript SDK for Stream Chat. It targets browser, Node, and React Native with conditional exports and multiple bundles (ESM & CJS). The public API is used by a number of downstream SDKs and' in text, "expected to find: " + 'Official JavaScript SDK for Stream Chat. It targets browser, Node, and React Native with conditional exports and multiple bundles (ESM & CJS). The public API is used by a number of downstream SDKs and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.' in text, "expected to find: " + 'Guidance for AI coding agents (Copilot, Cursor, Aider, Claude, etc.) working in this repository. Human readers are welcome, but this file is written for tools.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When altering public API, update inline docs and any affected guide pages in the docs site where this repo is the source of truth.' in text, "expected to find: " + '- When altering public API, update inline docs and any affected guide pages in the docs site where this repo is the source of truth.'[:80]

