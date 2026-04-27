"""Behavioral checks for worktrunk-docsrelease-integrate-cargosemverchecks-into-relea (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/worktrunk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert '4. **Check library API compatibility**: Run `cargo semver-checks check-release -p worktrunk` (install with `cargo install cargo-semver-checks --locked` if missing). If it reports breaking changes, the' in text, "expected to find: " + '4. **Check library API compatibility**: Run `cargo semver-checks check-release -p worktrunk` (install with `cargo install cargo-semver-checks --locked` if missing). If it reports breaking changes, the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert 'Worktrunk is primarily a CLI, but it also publishes a library crate (`[lib]` in `Cargo.toml`) that downstream crates depend on. `cargo-semver-checks` compares the current public API against the last v' in text, "expected to find: " + 'Worktrunk is primarily a CLI, but it also publishes a library crate (`[lib]` in `Cargo.toml`) that downstream crates depend on. `cargo-semver-checks` compares the current public API against the last v'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release/SKILL.md')
    assert "- **Tool fails to run** (e.g., missing baseline): likely the crate hasn't been published yet or the registry cache is stale. Try `cargo semver-checks check-release -p worktrunk --baseline-version <las" in text, "expected to find: " + "- **Tool fails to run** (e.g., missing baseline): likely the crate hasn't been published yet or the registry cache is stale. Try `cargo semver-checks check-release -p worktrunk --baseline-version <las"[:80]

