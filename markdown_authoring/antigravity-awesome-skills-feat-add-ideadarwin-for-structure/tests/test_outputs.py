"""Behavioral checks for antigravity-awesome-skills-feat-add-ideadarwin-for-structure (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/idea-darwin/SKILL.md')
    assert 'Most idea management tools are filing cabinets: they store ideas, tag them, and let them rot. Idea Darwin flips the paradigm — instead of organizing ideas, it lets them **compete**. Every idea is a li' in text, "expected to find: " + 'Most idea management tools are filing cabinets: they store ideas, tag them, and let them rot. Idea Darwin flips the paradigm — instead of organizing ideas, it lets them **compete**. Every idea is a li'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/idea-darwin/SKILL.md')
    assert 'description: "Darwinian idea evolution engine — toss rough ideas onto an evolution island, let them compete, crossbreed, and mutate through structured rounds to surface your strongest concepts."' in text, "expected to find: " + 'description: "Darwinian idea evolution engine — toss rough ideas onto an evolution island, let them compete, crossbreed, and mutate through structured rounds to surface your strongest concepts."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/idea-darwin/SKILL.md')
    assert 'A round-based idea iteration system that treats ideas as competing organisms — scoring, selecting, crossing, and evolving them through structured rounds to surface the strongest concepts.' in text, "expected to find: " + 'A round-based idea iteration system that treats ideas as competing organisms — scoring, selecting, crossing, and evolving them through structured rounds to surface the strongest concepts.'[:80]

