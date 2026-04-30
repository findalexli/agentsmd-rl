"""Behavioral checks for mina-rust-set-up-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mina-rust")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'using zero-knowledge proofs. It follows a Redux-style state machine architecture' in text, "expected to find: " + 'using zero-knowledge proofs. It follows a Redux-style state machine architecture'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Remember: This is a complex blockchain implementation. Take time to understand' in text, "expected to find: " + 'Remember: This is a complex blockchain implementation. Take time to understand'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **node/** - Main node logic (block production, transaction pool, consensus)' in text, "expected to find: " + '- **node/** - Main node logic (block production, transaction pool, consensus)'[:80]

