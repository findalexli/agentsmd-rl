"""Behavioral checks for web-dev-for-beginners-add-agentsmd-file-to-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/web-dev-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is an educational curriculum repository for teaching web development fundamentals to beginners. The curriculum is a comprehensive 12-week course developed by Microsoft Cloud Advocates, featuring ' in text, "expected to find: " + 'This is an educational curriculum repository for teaching web development fundamentals to beginners. The curriculum is a comprehensive 12-week course developed by Microsoft Cloud Advocates, featuring '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Practical Projects**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, and AI Chat Assistant' in text, "expected to find: " + '- **Practical Projects**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, and AI Chat Assistant'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recommended for learners' in text, "expected to find: " + '- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recommended for learners'[:80]

