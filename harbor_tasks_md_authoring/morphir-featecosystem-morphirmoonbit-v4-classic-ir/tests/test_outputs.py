"""Behavioral checks for morphir-featecosystem-morphirmoonbit-v4-classic-ir (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/morphir")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ecosystem/AGENTS.md')
    assert 'When morphir-go, morphir-python, or others are added, they will live under `ecosystem/` with the same pattern. Document any language- or repo-specific usage in this file.' in text, "expected to find: " + 'When morphir-go, morphir-python, or others are added, they will live under `ecosystem/` with the same pattern. Document any language- or repo-specific usage in this file.'[:80]

