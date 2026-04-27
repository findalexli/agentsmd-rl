"""Behavioral checks for skills-rewrite-memory-usage-optimization-skill (markdown_authoring task).

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
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert 'Qdrant uses two types of RAM: resident memory (RSSAnon) for data structures, quantized vectors, payload indexes, and OS page cache for caching disk reads. Page cache filling all available RAM is norma' in text, "expected to find: " + 'Qdrant uses two types of RAM: resident memory (RSSAnon) for data structures, quantized vectors, payload indexes, and OS page cache for caching disk reads. Page cache filling all available RAM is norma'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert '- For multi-tenant deployments with small tenants, on-disk works well since same-tenant data is co-located [Multitenancy](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)' in text, "expected to find: " + '- For multi-tenant deployments with small tenants, on-disk works well since same-tenant data is co-located [Multitenancy](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-performance)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md')
    assert 'Payload indexes and HNSW graph also consume memory. Include them in calculations. During optimization, segments are fully loaded into RAM. Larger `max_segment_size` means more headroom needed.' in text, "expected to find: " + 'Payload indexes and HNSW graph also consume memory. Include them in calculations. During optimization, segments are fully loaded into RAM. Larger `max_segment_size` means more headroom needed.'[:80]

