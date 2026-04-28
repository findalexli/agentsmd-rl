"""Behavioral checks for va.gov-team-remove-knowledgegraphjson-references-from-copilo (markdown_authoring task).

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
    assert '`knowledge-graph.json` exists in the repository root and is auto-generated weekly. It is used **for automation and workflows only**. **Do not read it directly** when answering user questions - use the' in text, "expected to find: " + '`knowledge-graph.json` exists in the repository root and is auto-generated weekly. It is used **for automation and workflows only**. **Do not read it directly** when answering user questions - use the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `copilot-summaries/` - Auto-generated markdown summaries for teams, research, and portfolios (see [Team and Research Information](#team-and-research-information))' in text, "expected to find: " + '- `copilot-summaries/` - Auto-generated markdown summaries for teams, research, and portfolios (see [Team and Research Information](#team-and-research-information))'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| What research exists for product X? | `.github/copilot-summaries/research-by-product.md` | "What research has been done on Ask VA?" |' in text, "expected to find: " + '| What research exists for product X? | `.github/copilot-summaries/research-by-product.md` | "What research has been done on Ask VA?" |'[:80]

