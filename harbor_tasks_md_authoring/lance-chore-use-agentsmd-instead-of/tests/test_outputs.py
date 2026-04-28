"""Behavioral checks for lance-chore-use-agentsmd-instead-of (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lance")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **Indexing**: Supports both vector indices (for similarity search) and scalar indices (BTree, inverted)' in text, "expected to find: " + '4. **Indexing**: Supports both vector indices (for similarity search) and scalar indices (BTree, inverted)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Lance is a modern columnar data format optimized for ML workflows and datasets. It provides:' in text, "expected to find: " + 'Lance is a modern columnar data format optimized for ML workflows and datasets. It provides:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Async-first Architecture**: Heavy use of tokio and async/await throughout Rust codebase' in text, "expected to find: " + '1. **Async-first Architecture**: Heavy use of tokio and async/await throughout Rust codebase'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert 'format: `./mvnw spotless:apply && cargo fmt --manifest-path ./lance-jni/Cargo.toml --all`' in text, "expected to find: " + 'format: `./mvnw spotless:apply && cargo fmt --manifest-path ./lance-jni/Cargo.toml --all`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert 'Use `./mvnw` instead of `mvn` to ensure the correct version of Maven is used.' in text, "expected to find: " + 'Use `./mvnw` instead of `mvn` to ensure the correct version of Maven is used.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('java/AGENTS.md')
    assert 'lint rust: `cargo clippy --tests --manifest-path ./lance-jni/Cargo.toml`' in text, "expected to find: " + 'lint rust: `cargo clippy --tests --manifest-path ./lance-jni/Cargo.toml`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('java/CLAUDE.md')
    assert 'java/CLAUDE.md' in text, "expected to find: " + 'java/CLAUDE.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('java/CLAUDE.md')
    assert 'java/CLAUDE.md' in text, "expected to find: " + 'java/CLAUDE.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('protos/AGENTS.md')
    assert "All changes should be backwards compatible. Don't re-use field numbers of change" in text, "expected to find: " + "All changes should be backwards compatible. Don't re-use field numbers of change"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('protos/AGENTS.md')
    assert 'field numbers of existing fields.' in text, "expected to find: " + 'field numbers of existing fields.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('protos/CLAUDE.md')
    assert 'protos/CLAUDE.md' in text, "expected to find: " + 'protos/CLAUDE.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('protos/CLAUDE.md')
    assert 'protos/CLAUDE.md' in text, "expected to find: " + 'protos/CLAUDE.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('python/AGENTS.md')
    assert '* Run single test: `pytest python/tests/<test_file>.py::<test_name>`' in text, "expected to find: " + '* Run single test: `pytest python/tests/<test_file>.py::<test_name>`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('python/AGENTS.md')
    assert 'Use the makefile for most actions:' in text, "expected to find: " + 'Use the makefile for most actions:'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('python/AGENTS.md')
    assert '* Build: `maturin develop`' in text, "expected to find: " + '* Build: `maturin develop`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('python/CLAUDE.md')
    assert 'python/CLAUDE.md' in text, "expected to find: " + 'python/CLAUDE.md'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('python/CLAUDE.md')
    assert 'python/CLAUDE.md' in text, "expected to find: " + 'python/CLAUDE.md'[:80]

