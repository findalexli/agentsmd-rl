"""Behavioral checks for erigon-teach-claude-skills-for-building (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/erigon")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-build/SKILL.md')
    assert 'description: Build the Erigon binary using make. Use this when you need to compile erigon before running any erigon commands.' in text, "expected to find: " + 'description: Build the Erigon binary using make. Use this when you need to compile erigon before running any erigon commands.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-build/SKILL.md')
    assert 'Build the Erigon binary by running `make erigon` from the repository root.' in text, "expected to find: " + 'Build the Erigon binary by running `make erigon` from the repository root.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-build/SKILL.md')
    assert 'This compiles the Erigon binary and places it at `./build/bin/erigon`.' in text, "expected to find: " + 'This compiles the Erigon binary and places it at `./build/bin/erigon`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-seg-retire/SKILL.md')
    assert 'description: Run the Erigon segment retire command to build, merge, and clean snapshot files. Use this for snapshot publication readiness preparation.' in text, "expected to find: " + 'description: Run the Erigon segment retire command to build, merge, and clean snapshot files. Use this for snapshot publication readiness preparation.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-seg-retire/SKILL.md')
    assert 'The `erigon seg retire` command prepares snapshot files for publication by performing build, merge, and cleanup operations on segment files.' in text, "expected to find: " + 'The `erigon seg retire` command prepares snapshot files for publication by performing build, merge, and cleanup operations on segment files.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/erigon-seg-retire/SKILL.md')
    assert '4. **Prune Ancient Blocks** - Removes block data from the database that has been successfully snapshotted' in text, "expected to find: " + '4. **Prune Ancient Blocks** - Removes block data from the database that has been successfully snapshotted'[:80]

