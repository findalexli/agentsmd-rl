"""Behavioral checks for moosestack-add-clickhouse-best-practices-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/moosestack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each rule includes MooseStack TypeScript/Python examples. When reviewing or implementing ClickHouse-related code, read relevant rule files and cite specific rules in your guidance.' in text, "expected to find: " + 'Each rule includes MooseStack TypeScript/Python examples. When reviewing or implementing ClickHouse-related code, read relevant rule files and cite specific rules in your guidance.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When working with MooseStack data models, ClickHouse schemas, queries, or configurations, reference the `moosestack-clickhouse-best-practices` skill. It contains rules covering:' in text, "expected to find: " + 'When working with MooseStack data models, ClickHouse schemas, queries, or configurations, reference the `moosestack-clickhouse-best-practices` skill. It contains rules covering:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Rust (CLI), TypeScript (libs/web), Python (lib), ClickHouse (OLAP), Redpanda/Kafka (streaming), Temporal (workflows), Redis (state)' in text, "expected to find: " + 'Rust (CLI), TypeScript (libs/web), Python (lib), ClickHouse (OLAP), Redpanda/Kafka (streaming), Temporal (workflows), Redis (state)'[:80]

