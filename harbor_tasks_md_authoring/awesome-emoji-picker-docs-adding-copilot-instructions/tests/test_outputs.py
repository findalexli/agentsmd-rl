"""Behavioral checks for awesome-emoji-picker-docs-adding-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-emoji-picker")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This project is a cross-browser WebExtension (Firefox, Chromium, Thunderbird) for emoji picking, clipboard, and page insertion. It is modular, uses modern JS, and is structured for maintainability and' in text, "expected to find: " + 'This project is a cross-browser WebExtension (Firefox, Chromium, Thunderbird) for emoji picking, clipboard, and page insertion. It is modular, uses modern JS, and is structured for maintainability and'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use `scripts/make.sh [browser]` to build a release ZIP for a specific browser (default: Firefox). This script copies the correct manifest and zips the extension, excluding dev/test files.' in text, "expected to find: " + '- Use `scripts/make.sh [browser]` to build a release ZIP for a specific browser (default: Firefox). This script copies the correct manifest and zips the extension, excluding dev/test files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Message types are defined in `src/common/modules/data/BrowserCommunicationTypes.js` as an object (used like an enum). Always use the exported constants, not raw strings.' in text, "expected to find: " + '- Message types are defined in `src/common/modules/data/BrowserCommunicationTypes.js` as an object (used like an enum). Always use the exported constants, not raw strings.'[:80]

