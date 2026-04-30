"""Behavioral checks for restate-agentsmd-updates (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/restate")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **Lint check** (if you modified Rust files): Run `cargo clippy --all-features --all-targets --workspace -- -D warnings` to check for lint warnings.' in text, "expected to find: " + '4. **Lint check** (if you modified Rust files): Run `cargo clippy --all-features --all-targets --workspace -- -D warnings` to check for lint warnings.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '6. If you are making changes to Cargo.toml files, make sure to also regenerate workspace-hack (cargo hakari generate)' in text, "expected to find: " + '6. If you are making changes to Cargo.toml files, make sure to also regenerate workspace-hack (cargo hakari generate)'[:80]

