"""Behavioral checks for skills-add-hybrid-search-skill (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert 'combining-searches/' in text, "expected to find: " + 'combining-searches/'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'hybrid-search/' in text, "expected to find: " + 'hybrid-search/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'search-types/' in text, "expected to find: " + 'search-types/'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/diagnosis/SKILL.md')
    assert 'Check [Qdrant team recommendations on how to choose an embedding model](https://search.qdrant.tech/md/articles/how-to-choose-an-embedding-model/).' in text, "expected to find: " + 'Check [Qdrant team recommendations on how to choose an embedding model](https://search.qdrant.tech/md/articles/how-to-choose-an-embedding-model/).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/diagnosis/SKILL.md')
    assert 'Test top 3 MTEB models on 100-1000 sample queries. [Hosted Qdrant inference](https://search.qdrant.tech/md/documentation/inference/)' in text, "expected to find: " + 'Test top 3 MTEB models on 100-1000 sample queries. [Hosted Qdrant inference](https://search.qdrant.tech/md/documentation/inference/)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'how to rerank?\', \'results are not relevant\', \'I don\'t get needed results from my dataset bu' in text, "expected to find: " + 'description: "Guides Qdrant search strategy selection. Use when someone asks \'should I use hybrid search?\', \'how to rerank?\', \'results are not relevant\', \'I don\'t get needed results from my dataset bu'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert '- See how to use [Multistage queries](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=multi-stage-queries), for example with late interaction rerankers through [Multivectors](http' in text, "expected to find: " + '- See how to use [Multistage queries](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=multi-stage-queries), for example with late interaction rerankers through [Multivectors](http'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/SKILL.md')
    assert 'Use when: pure vector search misses keyword/domain term matches, or the use case benefits from combining searches on multiple representations (including languages and modalities) of the same item.' in text, "expected to find: " + 'Use when: pure vector search misses keyword/domain term matches, or the use case benefits from combining searches on multiple representations (including languages and modalities) of the same item.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md')
    assert 'description: "Explains hybrid search in Qdrant. Use when someone asks \'how do I setup hybrid search?\', \'how to combine keyword and semantic search?\', \'sparse plus dense vectors?\', \'missing keyword mat' in text, "expected to find: " + 'description: "Explains hybrid search in Qdrant. Use when someone asks \'how do I setup hybrid search?\', \'how to combine keyword and semantic search?\', \'sparse plus dense vectors?\', \'missing keyword mat'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md')
    assert '2. Construct a hybrid search request with Query API from your building blocks. You can search independently among one type of vectors, with `prefetch` + `using`, like shown in examples in [Hybrid Quer' in text, "expected to find: " + '2. Construct a hybrid search request with Query API from your building blocks. You can search independently among one type of vectors, with `prefetch` + `using`, like shown in examples in [Hybrid Quer'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md')
    assert '1. Configure Qdrant collection with [named vectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=named-vectors), where each named vector usually corresponds to one representation' in text, "expected to find: " + '1. Configure Qdrant collection with [named vectors](https://search.qdrant.tech/md/documentation/manage-data/vectors/?s=named-vectors), where each named vector usually corresponds to one representation'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md')
    assert '- **[DBSF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=distribution-based-score-fusion-dbsf)** (Distribution-Based Score Fusion) — normalizes score distributions per prefetch ' in text, "expected to find: " + '- **[DBSF](https://search.qdrant.tech/md/documentation/search/hybrid-queries/?s=distribution-based-score-fusion-dbsf)** (Distribution-Based Score Fusion) — normalizes score distributions per prefetch '[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md')
    assert 'The outer query fuses ranked candidate lists from all parallel prefetches into one ranked list of results. Fusion methods differ in whether they use rank, score or directly vector representations of c' in text, "expected to find: " + 'The outer query fuses ranked candidate lists from all parallel prefetches into one ranked list of results. Fusion methods differ in whether they use rank, score or directly vector representations of c'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md')
    assert 'You can use any type of vector as an outer query over the prefetches, to perform the fusion on the server-side in one QueryAPI request: sparse, dense, multivector. For that, same type of vector repres' in text, "expected to find: " + 'You can use any type of vector as an outer query over the prefetches, to perform the fusion on the server-side in one QueryAPI request: sparse, dense, multivector. For that, same type of vector repres'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md')
    assert "If first, help user to design logic of constructing query or/and filters on application side and then check [Combining Searches](../combining-searches/SKILL.md). Don't forget to create [indices on fil" in text, "expected to find: " + "If first, help user to design logic of constructing query or/and filters on application side and then check [Combining Searches](../combining-searches/SKILL.md). Don't forget to create [indices on fil"[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md')
    assert '- **SPLADE++** learned sparse with term expansion. Heavier inference and resources usage but better performance due to term expansion. Requires fine-tuning for domain-specific retrieval. Provided in Q' in text, "expected to find: " + '- **SPLADE++** learned sparse with term expansion. Heavier inference and resources usage but better performance due to term expansion. Requires fine-tuning for domain-specific retrieval. Provided in Q'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md')
    assert '- **BM25** statistical representations, built into Qdrant core (computed server-side). Good baseline, works out-of-domain, usually for long texts. Can be used for non-English content, but needs to be ' in text, "expected to find: " + '- **BM25** statistical representations, built into Qdrant core (computed server-side). Good baseline, works out-of-domain, usually for long texts. Can be used for non-English content, but needs to be '[:80]

