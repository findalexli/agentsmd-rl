"""Behavioral checks for skills-scaling-skill (markdown_authoring task).

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
    text = _read('skills/qdrant-scaling/SKILL.md')
    assert 'description: "Guides Qdrant scaling decisions. Use when someone asks \'how many nodes do I need\', \'data doesn\'t fit on one node\', \'need more throughput\', \'cluster is slow\', \'too many tenants\', \'vertica' in text, "expected to find: " + 'description: "Guides Qdrant scaling decisions. Use when someone asks \'how many nodes do I need\', \'data doesn\'t fit on one node\', \'need more throughput\', \'cluster is slow\', \'too many tenants\', \'vertica'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/SKILL.md')
    assert "First determine what you're scaling for: data volume, query throughput (QPS), query latency, tenant count, or IOPS. Each pulls toward different strategies. Scaling for throughput and latency are oppos" in text, "expected to find: " + "First determine what you're scaling for: data volume, query throughput (QPS), query latency, tenant count, or IOPS. Each pulls toward different strategies. Scaling for throughput and latency are oppos"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/SKILL.md')
    assert 'Throughput (queries per second, QPS), latency, IOPS limitations, and memory pressure. Different dimensions that pull in different directions. [Performance Scaling](performance-scaling/SKILL.md)' in text, "expected to find: " + 'Throughput (queries per second, QPS), latency, IOPS limitations, and memory pressure. Different dimensions that pull in different directions. [Performance Scaling](performance-scaling/SKILL.md)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/horizontal-scaling/SKILL.md')
    assert 'description: "Diagnoses and guides Qdrant horizontal scaling decisions. Use when someone asks \'vertical or horizontal?\', \'how many nodes?\', \'how many shards?\', \'how to add nodes\', \'resharding\', \'data ' in text, "expected to find: " + 'description: "Diagnoses and guides Qdrant horizontal scaling decisions. Use when someone asks \'vertical or horizontal?\', \'how many nodes?\', \'how many shards?\', \'how to add nodes\', \'resharding\', \'data '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/horizontal-scaling/SKILL.md')
    assert 'Vertical first: simpler operations, no network overhead, good up to ~100M vectors per node depending on dimensions and quantization. Horizontal when: data exceeds single node capacity, need fault tole' in text, "expected to find: " + 'Vertical first: simpler operations, no network overhead, good up to ~100M vectors per node depending on dimensions and quantization. Horizontal when: data exceeds single node capacity, need fault tole'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/horizontal-scaling/SKILL.md')
    assert '- Estimate memory needs: `num_vectors * dimensions * 4 bytes * 1.5` plus payload and index overhead. Reserve 20% headroom for optimizations. [Capacity planning](https://qdrant.tech/documentation/guide' in text, "expected to find: " + '- Estimate memory needs: `num_vectors * dimensions * 4 bytes * 1.5` plus payload and index overhead. Reserve 20% headroom for optimizations. [Capacity planning](https://qdrant.tech/documentation/guide'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert 'description: "Diagnoses and guides Qdrant performance scaling for throughput, latency, IOPS, and memory pressure. Use when someone reports \'need more throughput\', \'need lower latency\', \'queries timeou' in text, "expected to find: " + 'description: "Diagnoses and guides Qdrant performance scaling for throughput, latency, IOPS, and memory pressure. Use when someone reports \'need more throughput\', \'need lower latency\', \'queries timeou'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert '- Configure delayed read fan-out (v1.17+) for tail latency in distributed clusters [Delayed fan-outs](https://qdrant.tech/documentation/guides/low-latency-search/#use-delayed-fan-outs)' in text, "expected to find: " + '- Configure delayed read fan-out (v1.17+) for tail latency in distributed clusters [Delayed fan-outs](https://qdrant.tech/documentation/guides/low-latency-search/#use-delayed-fan-outs)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert '- Configure update throughput control (v1.17+) to prevent unoptimized searches degrading reads [Low latency search](https://qdrant.tech/documentation/guides/low-latency-search/)' in text, "expected to find: " + '- Configure update throughput control (v1.17+) to prevent unoptimized searches degrading reads [Low latency search](https://qdrant.tech/documentation/guides/low-latency-search/)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/tenant-scaling/SKILL.md')
    assert 'description: "Guides Qdrant multi-tenant scaling. Use when someone asks \'how to scale tenants\', \'one collection per tenant?\', \'tenant isolation\', \'dedicated shards\', or reports tenant performance issu' in text, "expected to find: " + 'description: "Guides Qdrant multi-tenant scaling. Use when someone asks \'how to scale tenants\', \'one collection per tenant?\', \'tenant isolation\', \'dedicated shards\', or reports tenant performance issu'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/tenant-scaling/SKILL.md')
    assert 'Do not create one collection per tenant. Does not scale past a few hundred and wastes resources. One company hit the 1000 collection limit after a year of collection-per-repo and had to migrate to pay' in text, "expected to find: " + 'Do not create one collection per tenant. Does not scale past a few hundred and wastes resources. One company hit the 1000 collection limit after a year of collection-per-repo and had to migrate to pay'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/tenant-scaling/SKILL.md')
    assert '- Disable global HNSW (`m: 0`) and use `payload_m: 16` for per-tenant indexes, dramatically faster ingestion [Calibrate performance](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-pe' in text, "expected to find: " + '- Disable global HNSW (`m: 0`) and use `payload_m: 16` for per-tenant indexes, dramatically faster ingestion [Calibrate performance](https://qdrant.tech/documentation/guides/multitenancy/#calibrate-pe'[:80]

