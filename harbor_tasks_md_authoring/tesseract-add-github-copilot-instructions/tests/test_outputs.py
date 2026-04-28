"""Behavioral checks for tesseract-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tesseract")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Trust these instructions.** Only search for additional information if these instructions are incomplete, outdated, or if you encounter an error not covered here. The workflows and build procedures a' in text, "expected to find: " + '**Trust these instructions.** Only search for additional information if these instructions are incomplete, outdated, or if you encounter an error not covered here. The workflows and build procedures a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**CMake enforces out-of-source builds** - you cannot build in the source directory. If you get an error about this, remove `CMakeCache.txt` and build in a separate directory.' in text, "expected to find: " + '**CMake enforces out-of-source builds** - you cannot build in the source directory. If you get an error about this, remove `CMakeCache.txt` and build in a separate directory.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Tesseract is an open-source **OCR (Optical Character Recognition) engine** that recognizes text from images. This repository contains:' in text, "expected to find: " + 'Tesseract is an open-source **OCR (Optical Character Recognition) engine** that recognizes text from images. This repository contains:'[:80]

