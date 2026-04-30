"""Behavioral checks for obsidian-wiki-fix-tag-formatting-in-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-wiki")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/llm-wiki/SKILL.md')
    assert '- [[transformer-architecture]] — The dominant architecture for sequence modeling ( #ml #architecture)' in text, "expected to find: " + '- [[transformer-architecture]] — The dominant architecture for sequence modeling ( #ml #architecture)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/llm-wiki/SKILL.md')
    assert '- [[andrej-karpathy]] — AI researcher, educator, former Tesla AI director ( #person #ml)' in text, "expected to find: " + '- [[andrej-karpathy]] — AI researcher, educator, former Tesla AI director ( #person #ml)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/llm-wiki/SKILL.md')
    assert '- [[attention-mechanism]] — Core building block of transformers ( #ml #fundamentals)' in text, "expected to find: " + '- [[attention-mechanism]] — Core building block of transformers ( #ml #fundamentals)'[:80]

