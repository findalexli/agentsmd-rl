"""Behavioral checks for swc-chore-sync-claudemd-from-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '4. You can run fixture tests by doing `./scripts/test.sh`, and you can do `UPDATE=1 ./scripts/test.sh` to update fixtures.' in text, "expected to find: " + '4. You can run fixture tests by doing `./scripts/test.sh`, and you can do `UPDATE=1 ./scripts/test.sh` to update fixtures.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When working in a specific directory, apply the rules from that directory and all parent directories up to the root.' in text, "expected to find: " + 'When working in a specific directory, apply the rules from that directory and all parent directories up to the root.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. You can run execution tests by doing `./scripts/exec.sh` to see if your changes are working.' in text, "expected to find: " + '1. You can run execution tests by doing `./scripts/exec.sh` to see if your changes are working.'[:80]

