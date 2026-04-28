"""Behavioral checks for bitbox02-firmware-agentmd-improvements (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bitbox02-firmware")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Any shell command can be run inside docker using `./scripts/docker_exec.sh <command>` - do not use' in text, "expected to find: " + 'Any shell command can be run inside docker using `./scripts/docker_exec.sh <command>` - do not use'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For Rust code changes, run `cd src/rust && cargo fmt` to format the code.' in text, "expected to find: " + 'For Rust code changes, run `cd src/rust && cargo fmt` to format the code.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`bash -lc` before the command.' in text, "expected to find: " + '`bash -lc` before the command.'[:80]

