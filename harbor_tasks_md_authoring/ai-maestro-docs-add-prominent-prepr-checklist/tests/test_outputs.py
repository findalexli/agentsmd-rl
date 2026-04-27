"""Behavioral checks for ai-maestro-docs-add-prominent-prepr-checklist (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-maestro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**This is NON-NEGOTIABLE.** Every PR to main MUST include a version bump. No exceptions.' in text, "expected to find: " + '**This is NON-NEGOTIABLE.** Every PR to main MUST include a version bump. No exceptions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. ✅ **VERSION BUMPED** (see Pre-PR Checklist above - this should already be done)' in text, "expected to find: " + '1. ✅ **VERSION BUMPED** (see Pre-PR Checklist above - this should already be done)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**⚠️ STOP! Before creating ANY Pull Request to main, complete this checklist:**' in text, "expected to find: " + '**⚠️ STOP! Before creating ANY Pull Request to main, complete this checklist:**'[:80]

