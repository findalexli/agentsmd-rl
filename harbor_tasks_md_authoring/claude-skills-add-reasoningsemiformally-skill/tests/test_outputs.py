"""Behavioral checks for claude-skills-add-reasoningsemiformally-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert 'description: Apply semi-formal certificate reasoning to code analysis — patch verification, fault localization, patch equivalence. Use when reviewing patches, hunting bugs across scopes, comparing fix' in text, "expected to find: " + 'description: Apply semi-formal certificate reasoning to code analysis — patch verification, fault localization, patch equivalence. Use when reviewing patches, hunting bugs across scopes, comparing fix'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert 'These templates are **cognitive forcing functions**. They change what the model thinks about before concluding — not its reasoning ability. Standard chain-of-thought lets pattern-matching to plausible' in text, "expected to find: " + 'These templates are **cognitive forcing functions**. They change what the model thinks about before concluding — not its reasoning ability. Standard chain-of-thought lets pattern-matching to plausible'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('reasoning-semiformally/SKILL.md')
    assert '**Value scales with reasoning distance.** Locally-obvious bugs show no improvement. Cross-scope, cross-file, and architectural bugs show dramatic gains (+11pp fault localization in our experiments).' in text, "expected to find: " + '**Value scales with reasoning distance.** Locally-obvious bugs show no improvement. Cross-scope, cross-file, and architectural bugs show dramatic gains (+11pp fault localization in our experiments).'[:80]

