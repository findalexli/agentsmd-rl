"""Behavioral checks for diskann-add-agentsmd-onboarding-guide-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/diskann")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert 'DiskANN uses a baseline caching system for regression detection. See [`diskann/README.md`](diskann/README.md) for a high-level overview of how the baseline system works. For implementation and API det' in text, "expected to find: " + 'DiskANN uses a baseline caching system for regression detection. See [`diskann/README.md`](diskann/README.md) for a high-level overview of how the baseline system works. For implementation and API det'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '**Note**: CI uses `cargo-nextest` for running tests. See [`.cargo/nextest.toml`](.cargo/nextest.toml) for test configuration (timeouts, retries, etc.).' in text, "expected to find: " + '**Note**: CI uses `cargo-nextest` for running tests. See [`.cargo/nextest.toml`](.cargo/nextest.toml) for test configuration (timeouts, retries, etc.).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agents.md')
    assert '**DiskANN** is a Rust implementation of scalable approximate nearest neighbor (ANN) search algorithms. The project is a rewrite from C++ to Rust.' in text, "expected to find: " + '**DiskANN** is a Rust implementation of scalable approximate nearest neighbor (ANN) search algorithms. The project is a rewrite from C++ to Rust.'[:80]

