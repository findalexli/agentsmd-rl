"""Behavioral checks for oxc-choreall-add-a-skillmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oxc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insta-snapshots/SKILL.md')
    assert 'New snapshots are stored as `.snap.new` files next to their corresponding `.snap` files. You can use `cargo insta pending-snapshots` to view the changes to the snapshot files.' in text, "expected to find: " + 'New snapshots are stored as `.snap.new` files next to their corresponding `.snap` files. You can use `cargo insta pending-snapshots` to view the changes to the snapshot files.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insta-snapshots/SKILL.md')
    assert 'Note that `.snap.md` files are from Vitest, and **not** Insta. They are used in conformance tests, and are not handled by the instructions in this skill.' in text, "expected to find: " + 'Note that `.snap.md` files are from Vitest, and **not** Insta. They are used in conformance tests, and are not handled by the instructions in this skill.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insta-snapshots/SKILL.md')
    assert 'Snapshots track **expected test outputs** (often failures or errors). When code changes, new snapshots are generated as `.snap.new` files for review.' in text, "expected to find: " + 'Snapshots track **expected test outputs** (often failures or errors). When code changes, new snapshots are generated as `.snap.new` files for review.'[:80]

