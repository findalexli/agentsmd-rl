"""Behavioral checks for skills-refine-qdrant-search-strategies-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'BM25 or sparse vectors?\', \'how to rerank?\', \'results are not relevant\', \'I don\'t get needed' in text, "expected to find: " + 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'BM25 or sparse vectors?\', \'how to rerank?\', \'results are not relevant\', \'I don\'t get needed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert "Relevance Feedback (RF) Query uses a feedback model's scores on retrieved results to steer the retriever through the full vector space on subsequent iterations, like reranking the entire collection th" in text, "expected to find: " + "Relevance Feedback (RF) Query uses a feedback model's scores on retrieved results to steer the retriever through the full vector space on subsequent iterations, like reranking the entire collection th"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert "- ColBERT and ColPali/ColQwen reranking is especially precise due to late interaction mechanisms, however, heavy. It's important to configure & store multivectors without building HNSW for them, to sa" in text, "expected to find: " + "- ColBERT and ColPali/ColQwen reranking is especially precise due to late interaction mechanisms, however, heavy. It's important to configure & store multivectors without building HNSW for them, to sa"[:80]

