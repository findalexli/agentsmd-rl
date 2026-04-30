"""Behavioral checks for copilot-collections-clarify-codebaseanalysis-skill-usage-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/copilot-collections")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/code-quality-check.prompt.md')
    assert '- `codebase-analysis` - for the structured codebase analysis process only (note: this prompt\'s "Report Structure" section overrides any report/template instructions from the skill)' in text, "expected to find: " + '- `codebase-analysis` - for the structured codebase analysis process only (note: this prompt\'s "Report Structure" section overrides any report/template instructions from the skill)'[:80]

