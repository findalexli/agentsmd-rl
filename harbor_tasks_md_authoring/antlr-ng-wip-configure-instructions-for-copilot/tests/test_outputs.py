"""Behavioral checks for antlr-ng-wip-configure-instructions-for-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antlr-ng")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "antlr-ng (ANTLR Next Generation) is a TypeScript-based parser generator that translates grammar files into parser and lexer classes for multiple target languages. It's a production-ready port and enha" in text, "expected to find: " + "antlr-ng (ANTLR Next Generation) is a TypeScript-based parser generator that translates grammar files into parser and lexer classes for multiple target languages. It's a production-ready port and enha"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '10. **Member ordering**: Static fields → instance fields → constructor → public methods → private methods' in text, "expected to find: " + '10. **Member ordering**: Static fields → instance fields → constructor → public methods → private methods'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **src/codegen/target/**: Language-specific target implementations (Java, TypeScript, Python3, etc.)' in text, "expected to find: " + '- **src/codegen/target/**: Language-specific target implementations (Java, TypeScript, Python3, etc.)'[:80]

