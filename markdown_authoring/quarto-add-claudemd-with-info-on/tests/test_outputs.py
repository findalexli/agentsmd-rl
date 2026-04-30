"""Behavioral checks for quarto-add-claudemd-with-info-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quarto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'Quarto is an open-source scientific and technical publishing system built on [Pandoc](https://pandoc.org). This repository contains the source code for various parts of the Quarto ecosystem, with the ' in text, "expected to find: " + 'Quarto is an open-source scientific and technical publishing system built on [Pandoc](https://pandoc.org). This repository contains the source code for various parts of the Quarto ecosystem, with the '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert '- VS Code extension: [apps/vscode/CONTRIBUTING.md](apps/vscode/CONTRIBUTING.md) - Contains detailed instructions for building, debugging, and releasing the extension' in text, "expected to find: " + '- VS Code extension: [apps/vscode/CONTRIBUTING.md](apps/vscode/CONTRIBUTING.md) - Contains detailed instructions for building, debugging, and releasing the extension'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('claude.md')
    assert 'The turborepo pipeline helps optimize build times by caching build artifacts and respecting the dependency graph between packages.' in text, "expected to find: " + 'The turborepo pipeline helps optimize build times by caching build artifacts and respecting the dependency graph between packages.'[:80]

