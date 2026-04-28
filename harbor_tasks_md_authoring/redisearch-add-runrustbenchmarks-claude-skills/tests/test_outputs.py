"""Behavioral checks for redisearch-add-runrustbenchmarks-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redisearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/run-rust-benchmarks/SKILL.md')
    assert '- `<crate> <bench>`: Run specific bench in a benchmakr crate (e.g., `/run-rust-benchmarks rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"`)' in text, "expected to find: " + '- `<crate> <bench>`: Run specific bench in a benchmakr crate (e.g., `/run-rust-benchmarks rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/run-rust-benchmarks/SKILL.md')
    assert '2. Once the benchmarks are complete, generate a summary comparing the average run times between the Rust and C implementations.' in text, "expected to find: " + '2. Once the benchmarks are complete, generate a summary comparing the average run times between the Rust and C implementations.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/run-rust-benchmarks/SKILL.md')
    assert 'cd src/redisearch_rs && cargo bench -p rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"' in text, "expected to find: " + 'cd src/redisearch_rs && cargo bench -p rqe_iterators_bencher "Iterator - InvertedIndex - Numeric - Read Dense"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/run-rust-tests/SKILL.md')
    assert '- `<crate> <test>`: Run specific test in crate (e.g., `/run-rust-tests hyperloglog test_merge`)' in text, "expected to find: " + '- `<crate> <test>`: Run specific test in crate (e.g., `/run-rust-tests hyperloglog test_merge`)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/run-rust-tests/SKILL.md')
    assert '- `<crate>`: Run tests for specific crate (e.g., `/run-rust-tests hyperloglog`)' in text, "expected to find: " + '- `<crate>`: Run tests for specific crate (e.g., `/run-rust-tests hyperloglog`)'[:80]

