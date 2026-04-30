"""Behavioral checks for pg-aiguide-apisignature-fixes-for-setuptimescaledbhypertable (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pg-aiguide")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert "**IMPORTANT**: If you used `tsdb.enable_columnstore=true` in Step 1, starting with TimescaleDB version 2.23 a columnstore policy is **automatically created** with `after => INTERVAL '7 days'`. You onl" in text, "expected to find: " + "**IMPORTANT**: If you used `tsdb.enable_columnstore=true` in Step 1, starting with TimescaleDB version 2.23 a columnstore policy is **automatically created** with `after => INTERVAL '7 days'`. You onl"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert '-- In TimescaleDB 2.23 and later only needed if you want to override the default 7-day policy created by tsdb.enable_columnstore=true' in text, "expected to find: " + '-- In TimescaleDB 2.23 and later only needed if you want to override the default 7-day policy created by tsdb.enable_columnstore=true'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/setup-timescaledb-hypertables/SKILL.md')
    assert 'ROUND(100.0 * (1 - after_compression_total_bytes::numeric / NULLIF(before_compression_total_bytes, 0)), 1) as compression_pct' in text, "expected to find: " + 'ROUND(100.0 * (1 - after_compression_total_bytes::numeric / NULLIF(before_compression_total_bytes, 0)), 1) as compression_pct'[:80]

