"""Behavioral checks for skills-reorg-scaling-skills (markdown_authoring task).

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
    assert 'Vertical scaling, horizontal scaling, throughput, latency, IOPS, and memory pressure. Start vertical, go horizontal only when necessary -- horizontal scaling is effectively a one-way street. [Performa' in text, "expected to find: " + 'Vertical scaling, horizontal scaling, throughput, latency, IOPS, and memory pressure. Start vertical, go horizontal only when necessary -- horizontal scaling is effectively a one-way street. [Performa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/SKILL.md')
    assert 'Multi-tenant workloads with payload partitioning, per-tenant indexes, and tiered multitenancy. [Tenant Scaling](tenant-scaling/SKILL.md)' in text, "expected to find: " + 'Multi-tenant workloads with payload partitioning, per-tenant indexes, and tiered multitenancy. [Tenant Scaling](tenant-scaling/SKILL.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/SKILL.md')
    assert '## Performance & Capacity Scaling' in text, "expected to find: " + '## Performance & Capacity Scaling'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert '**Start vertical, go horizontal only when you must.** Horizontal scaling adds permanent operational complexity -- sharding, replication, rebalancing, network overhead -- and is effectively a one-way s' in text, "expected to find: " + '**Start vertical, go horizontal only when you must.** Horizontal scaling adds permanent operational complexity -- sharding, replication, rebalancing, network overhead -- and is effectively a one-way s'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert 'description: "Guides Qdrant scaling decisions for capacity and performance. Use when someone asks about vertical vs horizontal scaling, node sizing, throughput, latency, IOPS, memory pressure, \'how to' in text, "expected to find: " + 'description: "Guides Qdrant scaling decisions for capacity and performance. Use when someone asks about vertical vs horizontal scaling, node sizing, throughput, latency, IOPS, memory pressure, \'how to'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/SKILL.md')
    assert "- **Data volume:** How much data needs to fit? RAM, disk, and quantization are the levers. Start with vertical (bigger nodes, quantization, mmap). Go horizontal only when a single node can't hold the " in text, "expected to find: " + "- **Data volume:** How much data needs to fit? RAM, disk, and quantization are the levers. Start with vertical (bigger nodes, quantization, mmap). Go horizontal only when a single node can't hold the "[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md')
    assert 'skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md' in text, "expected to find: " + 'skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md')
    assert 'description: "Guides Qdrant vertical scaling decisions. Use when someone asks \'how to scale up a node\', \'need more RAM\', \'upgrade node size\', \'vertical scaling\', \'resize cluster\', \'scale up vs scale o' in text, "expected to find: " + 'description: "Guides Qdrant vertical scaling decisions. Use when someone asks \'how to scale up a node\', \'need more RAM\', \'upgrade node size\', \'vertical scaling\', \'resize cluster\', \'scale up vs scale o'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md')
    assert 'Vertical scaling means increasing CPU, RAM, or disk on existing nodes rather than adding more nodes. This is the recommended first step before considering horizontal scaling. Vertical scaling is simpl' in text, "expected to find: " + 'Vertical scaling means increasing CPU, RAM, or disk on existing nodes rather than adding more nodes. This is the recommended first step before considering horizontal scaling. Vertical scaling is simpl'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md')
    assert '**Important:** Scaling up is straightforward. Scaling down requires care -- if the working set no longer fits in RAM after downsizing, performance will degrade severely due to cache eviction. Always l' in text, "expected to find: " + '**Important:** Scaling up is straightforward. Scaling down requires care -- if the working set no longer fits in RAM after downsizing, performance will degrade severely due to cache eviction. Always l'[:80]

