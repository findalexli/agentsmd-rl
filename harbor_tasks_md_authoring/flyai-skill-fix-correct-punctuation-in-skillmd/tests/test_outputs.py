"""Behavioral checks for flyai-skill-fix-correct-punctuation-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flyai-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flyai/SKILL.md')
    assert '- **AI search** (`ai-search`): Semantic search for hotels, flights, etc. Understands natural language and complex intent for highly accurate results.' in text, "expected to find: " + '- **AI search** (`ai-search`): Semantic search for hotels, flights, etc. Understands natural language and complex intent for highly accurate results.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flyai/SKILL.md')
    assert '1. **Install CLI**: `npm i -g @fly-ai/flyai-cli`' in text, "expected to find: " + '1. **Install CLI**: `npm i -g @fly-ai/flyai-cli`'[:80]

