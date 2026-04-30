"""Behavioral checks for jwx-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jwx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**NEVER edit files ending in `_gen.go` directly.** These are generated files. Edit the generator sources instead.' in text, "expected to find: " + '**NEVER edit files ending in `_gen.go` directly.** These are generated files. Edit the generator sources instead.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains multiple Go modules. The nested modules use `replace` directives for local development.' in text, "expected to find: " + 'This repository contains multiple Go modules. The nested modules use `replace` directives for local development.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository uses a **flat layout** with vanity import paths. There is no physical `v3/` directory.' in text, "expected to find: " + 'This repository uses a **flat layout** with vanity import paths. There is no physical `v3/` directory.'[:80]

