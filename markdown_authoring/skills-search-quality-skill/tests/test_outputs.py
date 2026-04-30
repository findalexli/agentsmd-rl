"""Behavioral checks for skills-search-quality-skill (markdown_authoring task).

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
    text = _read('skills/qdrant-search-quality/SKILL.md')
    assert 'description: "Diagnoses and improves Qdrant search relevance. Use when someone reports \'search results are bad\', \'wrong results\', \'low precision\', \'low recall\', \'irrelevant matches\', \'missing expected' in text, "expected to find: " + 'description: "Diagnoses and improves Qdrant search relevance. Use when someone reports \'search results are bad\', \'wrong results\', \'low precision\', \'low recall\', \'irrelevant matches\', \'missing expected'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/SKILL.md')
    assert 'First determine whether the problem is the embedding model, Qdrant configuration, or the query strategy. Most quality issues come from the model or data, not from Qdrant itself. If search quality is l' in text, "expected to find: " + 'First determine whether the problem is the embedding model, Qdrant configuration, or the query strategy. Most quality issues come from the model or data, not from Qdrant itself. If search quality is l'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/SKILL.md')
    assert 'Hybrid search, reranking, relevance feedback, and exploration APIs for improving result quality. [Search Strategies](search-strategies/SKILL.md)' in text, "expected to find: " + 'Hybrid search, reranking, relevance feedback, and exploration APIs for improving result quality. [Search Strategies](search-strategies/SKILL.md)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/diagnosis/SKILL.md')
    assert 'description: "Diagnoses Qdrant search quality issues. Use when someone reports \'results are bad\', \'wrong results\', \'missing matches\', \'recall is low\', \'approximate search worse than exact\', \'which emb' in text, "expected to find: " + 'description: "Diagnoses Qdrant search quality issues. Use when someone reports \'results are bad\', \'wrong results\', \'missing matches\', \'recall is low\', \'approximate search worse than exact\', \'which emb'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/diagnosis/SKILL.md')
    assert 'Binary quantization requires rescore. Without it, quality loss is severe. Use oversampling (3-5x minimum for binary) to recover recall. Always test quantization impact on your data before production. ' in text, "expected to find: " + 'Binary quantization requires rescore. Without it, quality loss is severe. Use oversampling (3-5x minimum for binary) to recover recall. Always test quantization impact on your data before production. '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/diagnosis/SKILL.md')
    assert 'Payload filtering and sparse vector search are different things. Metadata (dates, categories, tags) goes in payload for filtering. Text content goes in vectors for search. Do not embed metadata.' in text, "expected to find: " + 'Payload filtering and sparse vector search are different things. Metadata (dates, categories, tags) goes in payload for filtering. Text content goes in vectors for search. Do not embed metadata.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'BM25 or sparse vectors?\', \'how to rerank?\', \'results too similar\', \'need diversity\', \'MMR\',' in text, "expected to find: " + 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'BM25 or sparse vectors?\', \'how to rerank?\', \'results too similar\', \'need diversity\', \'MMR\','[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert 'Use hybrid when: domain terminology not in embedding training data, exact keyword matching critical (brand names, SKUs), acronyms common. Skip when: pure semantic queries, all data in training set, la' in text, "expected to find: " + 'Use hybrid when: domain terminology not in embedding training data, exact keyword matching critical (brand names, SKUs), acronyms common. Skip when: pure semantic queries, all data in training set, la'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert '- DBSF with asymmetric limits (sparse_limit=250, dense_limit=100) can outperform RRF for technical docs [DBSF](https://qdrant.tech/documentation/concepts/hybrid-queries/#distribution-based-score-fusio' in text, "expected to find: " + '- DBSF with asymmetric limits (sparse_limit=250, dense_limit=100) can outperform RRF for technical docs [DBSF](https://qdrant.tech/documentation/concepts/hybrid-queries/#distribution-based-score-fusio'[:80]

