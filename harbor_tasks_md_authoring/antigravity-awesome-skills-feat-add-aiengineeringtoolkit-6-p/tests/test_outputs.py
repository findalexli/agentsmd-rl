"""Behavioral checks for antigravity-awesome-skills-feat-add-aiengineeringtoolkit-6-p (markdown_authoring task).

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
    text = _read('skills/ai-engineering-toolkit/SKILL.md')
    assert 'Executes a 65-point red-team audit across 5 attack categories: direct prompt injection, indirect prompt injection (via RAG documents), information extraction (system prompt / API key leakage), tool ab' in text, "expected to find: " + 'Executes a 65-point red-team audit across 5 attack categories: direct prompt injection, indirect prompt injection (via RAG documents), information extraction (system prompt / API key leakage), tool ab'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-engineering-toolkit/SKILL.md')
    assert 'Scores prompts across 8 dimensions (Clarity, Specificity, Completeness, Conciseness, Structure, Grounding, Safety, Robustness) on a 1-10 scale with weighted aggregation to a 0-100 score. Identifies th' in text, "expected to find: " + 'Scores prompts across 8 dimensions (Clarity, Specificity, Completeness, Conciseness, Structure, Grounding, Safety, Robustness) on a 1-10 scale with weighted aggregation to a 0-100 score. Identifies th'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-engineering-toolkit/SKILL.md')
    assert 'Walks through a complete architecture decision tree: document format → parsing strategy → chunking approach (fixed/semantic/recursive) → embedding model selection → retrieval method (vector/keyword/hy' in text, "expected to find: " + 'Walks through a complete architecture decision tree: document format → parsing strategy → chunking approach (fixed/semantic/recursive) → embedding model selection → retrieval method (vector/keyword/hy'[:80]

