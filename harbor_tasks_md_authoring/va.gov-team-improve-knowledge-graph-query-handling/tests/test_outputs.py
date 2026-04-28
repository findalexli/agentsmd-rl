"""Behavioral checks for va.gov-team-improve-knowledge-graph-query-handling (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/va.gov-team")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Symptom:** You asked a question about teams, products, or research, and Copilot made multiple tool calls but provided no answer. You had to ask "What is the answer?" to get a response.' in text, "expected to find: " + '**Symptom:** You asked a question about teams, products, or research, and Copilot made multiple tool calls but provided no answer. You had to ask "What is the answer?" to get a response.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| "Which products are in Y portfolio?" | Lexical search | `"portfolio-digital-experience" "belongs_to_portfolio"` in knowledge-graph.json |' in text, "expected to find: " + '| "Which products are in Y portfolio?" | Lexical search | `"portfolio-digital-experience" "belongs_to_portfolio"` in knowledge-graph.json |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "**Important**: If you've made multiple tool calls and gathered sufficient information to answer the user's question," in text, "expected to find: " + "**Important**: If you've made multiple tool calls and gathered sufficient information to answer the user's question,"[:80]

