"""Behavioral checks for nettacker-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nettacker")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Think of AGENTS.md as a README for AI agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.' in text, "expected to find: " + 'Think of AGENTS.md as a README for AI agents: a dedicated, predictable place to provide the context and instructions to help AI coding agents work on your project.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs: include a clear description, rationale, linked issue(s), test evidence (logs or screenshots for web UI), and update docs if behavior changes.' in text, "expected to find: " + '- PRs: include a clear description, rationale, linked issue(s), test evidence (logs or screenshots for web UI), and update docs if behavior changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Source: `nettacker/` (CLI: `nettacker/main.py`, API: `nettacker/api/`, core libs: `nettacker/core/`, modules: `nettacker/modules/`).' in text, "expected to find: " + '- Source: `nettacker/` (CLI: `nettacker/main.py`, API: `nettacker/api/`, core libs: `nettacker/core/`, modules: `nettacker/modules/`).'[:80]

