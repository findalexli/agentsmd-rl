"""Behavioral checks for nx.js-docs-add-agentsmd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nx.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'A JavaScript runtime for **Nintendo Switch homebrew**, built on QuickJS + libnx + cairo. It implements Web APIs (Canvas 2D, Fetch, Crypto, URL, EventTarget, etc.) so you can write Switch apps in JS/TS' in text, "expected to find: " + 'A JavaScript runtime for **Nintendo Switch homebrew**, built on QuickJS + libnx + cairo. It implements Web APIs (Canvas 2D, Fetch, Crypto, URL, EventTarget, etc.) so you can write Switch apps in JS/TS'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- All packages in `@nx.js/runtime`, `@nx.js/nro`, `@nx.js/nsp`, and `create-nxjs-app` are version-locked (see `.changeset/config.json` `fixed` array)' in text, "expected to find: " + '- All packages in `@nx.js/runtime`, `@nx.js/nro`, `@nx.js/nsp`, and `create-nxjs-app` are version-locked (see `.changeset/config.json` `fixed` array)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Use `git worktree`** if working on multiple branches simultaneously — never share a working directory between parallel tasks' in text, "expected to find: " + '- **Use `git worktree`** if working on multiple branches simultaneously — never share a working directory between parallel tasks'[:80]

