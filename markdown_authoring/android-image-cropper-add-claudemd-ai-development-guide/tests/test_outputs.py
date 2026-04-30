"""Behavioral checks for android-image-cropper-add-claudemd-ai-development-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/android-image-cropper")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This document provides project-specific instructions for AI-assisted development on the Android Image Cropper library.' in text, "expected to find: " + 'This document provides project-specific instructions for AI-assisted development on the Android Image Cropper library.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Branch Naming**: Use developer github name `canato/` prefix (e.g., `canato/fix-rotation-bug`)' in text, "expected to find: " + '1. **Branch Naming**: Use developer github name `canato/` prefix (e.g., `canato/fix-rotation-bug`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '*This document is maintained for AI-assisted development. Keep it updated as the project evolves.*' in text, "expected to find: " + '*This document is maintained for AI-assisted development. Keep it updated as the project evolves.*'[:80]

