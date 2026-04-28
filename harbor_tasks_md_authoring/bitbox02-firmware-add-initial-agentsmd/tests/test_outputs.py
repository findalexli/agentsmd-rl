"""Behavioral checks for bitbox02-firmware-add-initial-agentsmd (markdown_authoring task).

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
    assert 'All make commands are to be run inside docker like this: `./scripts/docker_exec.sh make -j <command>`, e.g.  `./scripts/docker_exec.sh make -j firmware`.' in text, "expected to find: " + 'All make commands are to be run inside docker like this: `./scripts/docker_exec.sh make -j <command>`, e.g.  `./scripts/docker_exec.sh make -j firmware`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- In Rust unit tests, if testing a function foo, name the test `test_foo` (or `test_foo_xyz` if it needs qualifiers).' in text, "expected to find: " + '- In Rust unit tests, if testing a function foo, name the test `test_foo` (or `test_foo_xyz` if it needs qualifiers).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For C code changes, run ./scripts/format to format the code. For Python changes, run `black` to format the code.' in text, "expected to find: " + 'For C code changes, run ./scripts/format to format the code. For Python changes, run `black` to format the code.'[:80]

