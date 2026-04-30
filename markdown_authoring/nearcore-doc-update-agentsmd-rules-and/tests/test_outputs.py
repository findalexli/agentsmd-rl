"""Behavioral checks for nearcore-doc-update-agentsmd-rules-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nearcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- To run specific tests, use `cargo test --package {package} --features test_features -- {path::to::test} --exact --show-output`. Always use `--features test_features`. Use `--feature nightly` if need' in text, "expected to find: " + '- To run specific tests, use `cargo test --package {package} --features test_features -- {path::to::test} --exact --show-output`. Always use `--features test_features`. Use `--feature nightly` if need'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run exact command `RUSTFLAGS="-D warnings" cargo clippy --all-features --all-targets`' in text, "expected to find: " + '- Run exact command `RUSTFLAGS="-D warnings" cargo clippy --all-features --all-targets`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always prefer `use` declarations over fully qualified paths.' in text, "expected to find: " + '- Always prefer `use` declarations over fully qualified paths.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('chain/chain/CLAUDE.md')
    assert '- Synchronous preprocessing in `preprocess_block` validates in this order: block signature → header → block body → chunk headers → chunk endorsements (>2/3 stake per chunk for non-SPICE) → missing chu' in text, "expected to find: " + '- Synchronous preprocessing in `preprocess_block` validates in this order: block signature → header → block body → chunk headers → chunk endorsements (>2/3 stake per chunk for non-SPICE) → missing chu'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('chain/chain/CLAUDE.md')
    assert '- Optimistic blocks allow chunk application to start before the full block arrives; cached results are reused during normal block processing. See `docs/architecture/how/optimistic_block.md`. Disabled ' in text, "expected to find: " + '- Optimistic blocks allow chunk application to start before the full block arrives; cached results are reused during normal block processing. See `docs/architecture/how/optimistic_block.md`. Disabled '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('chain/chain/CLAUDE.md')
    assert '- After validation, chunk application runs asynchronously on a rayon thread pool; postprocessing saves state and updates head.' in text, "expected to find: " + '- After validation, chunk application runs asynchronously on a rayon thread pool; postprocessing saves state and updates head.'[:80]

