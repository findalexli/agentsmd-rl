"""Behavioral checks for hyperlane-explorer-docs-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperlane-explorer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Hyperlane Explorer is a Next.js 15 web application for exploring interchain messages on the Hyperlane protocol. It allows users to search, view, and debug cross-chain messages.' in text, "expected to find: " + 'Hyperlane Explorer is a Next.js 15 web application for exploring interchain messages on the Hyperlane protocol. It allows users to search, view, and debug cross-chain messages.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Zustand store** (`src/store.ts`) manages global state: chain metadata, MultiProtocolProvider, warp routes' in text, "expected to find: " + '- **Zustand store** (`src/store.ts`) manages global state: chain metadata, MultiProtocolProvider, warp routes'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]

