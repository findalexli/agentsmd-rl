"""Behavioral checks for nanvix-ci-updating-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanvix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Order sections: Configuration (`#![...]`), Imports, Modules, Constants, Structures, Enumerations, Trait Implementations, Standalone Functions, Tests.' in text, "expected to find: " + '- Order sections: Configuration (`#![...]`), Imports, Modules, Constants, Structures, Enumerations, Trait Implementations, Standalone Functions, Tests.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use section header comments with `//==================================================================================================`.' in text, "expected to find: " + '- Use section header comments with `//==================================================================================================`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Always add explicit type annotation when defining variables and constants, even if type can be inferred (e.g., `let x: u32 = 42;`).' in text, "expected to find: " + '- Always add explicit type annotation when defining variables and constants, even if type can be inferred (e.g., `let x: u32 = 42;`).'[:80]

