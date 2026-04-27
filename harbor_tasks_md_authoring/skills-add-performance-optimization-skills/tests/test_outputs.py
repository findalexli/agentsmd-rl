"""Behavioral checks for skills-add-performance-optimization-skills (markdown_authoring task).

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
    text = _read('skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md')
    assert 'description: "Diagnoses and fixes slow Qdrant indexing and data ingestion. Use when someone reports \'uploads are slow\', \'indexing takes forever\', \'optimizer is stuck\', \'HNSW build time too long\', or \'' in text, "expected to find: " + 'description: "Diagnoses and fixes slow Qdrant indexing and data ingestion. Use when someone reports \'uploads are slow\', \'indexing takes forever\', \'optimizer is stuck\', \'HNSW build time too long\', or \''[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md')
    assert 'If you have a multi-tenant use-case, where all data is split by some payload field (e.g. `tenant_id`), you can avoid building global HNSW index and instead rely on `payload_m` value to only build HNSW' in text, "expected to find: " + 'If you have a multi-tenant use-case, where all data is split by some payload field (e.g. `tenant_id`), you can avoid building global HNSW index and instead rely on `payload_m` value to only build HNSW'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md')
    assert 'Qdrant does NOT build HNSW indexes immediately. Small segments use brute-force until they exceed `indexing_threshold_kb` (default: 20 MB). Search during this window is slower by design, not a bug.' in text, "expected to find: " + 'Qdrant does NOT build HNSW indexes immediately. Small segments use brute-force until they exceed `indexing_threshold_kb` (default: 20 MB). Search during this window is slower by design, not a bug.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert 'description: "Diagnoses and reduces Qdrant memory usage. Use when someone reports \'memory too high\', \'RAM keeps growing\', \'node crashed\', \'out of memory\', \'memory leak\', or asks \'why is memory usage s' in text, "expected to find: " + 'description: "Diagnoses and reduces Qdrant memory usage. Use when someone reports \'memory too high\', \'RAM keeps growing\', \'node crashed\', \'out of memory\', \'memory leak\', or asks \'why is memory usage s'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more abou' in text, "expected to find: " + '- For low RAM environments, consider `async_scorer` config, which enables support of `io_uring` for parallel disk access, which can significantly improve performance of on-disk storage. Read more abou'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inferece: [MRL docs](https://q' in text, "expected to find: " + '- Leverage Matryoshka Representation Learning (MRL) to store only small vectors in RAM, while keeping large vectors on disk. Examples of how to use MRL with qdrant cloud inferece: [MRL docs](https://q'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md')
    assert 'description: "Diagnoses and fixes slow Qdrant search. Use when someone reports \'search is slow\', \'high latency\', \'queries take too long\', \'low QPS\', \'throughput too low\', \'filtered search is slow\', or' in text, "expected to find: " + 'description: "Diagnoses and fixes slow Qdrant search. Use when someone reports \'search is slow\', \'high latency\', \'queries take too long\', \'low QPS\', \'throughput too low\', \'filtered search is slow\', or'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md')
    assert 'First determine whether the problem is latency (single query speed) or throughput (queries per second). These pull in opposite directions. Getting this wrong means tuning the wrong knob.' in text, "expected to find: " + 'First determine whether the problem is latency (single query speed) or throughput (queries per second). These pull in opposite directions. Getting this wrong means tuning the wrong knob.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md')
    assert '- Use oversampling + rescore for high-dimensional vectors [Search with quantization](https://qdrant.tech/documentation/guides/quantization/#searching-with-quantization)' in text, "expected to find: " + '- Use oversampling + rescore for high-dimensional vectors [Search with quantization](https://qdrant.tech/documentation/guides/quantization/#searching-with-quantization)'[:80]

