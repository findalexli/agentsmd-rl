"""Behavioral checks for jazz-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jazz")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Jazz is a distributed database framework for building local-first apps. It syncs data across frontends, serverless functions, and backend servers with real-time collaboration, offline support, and end' in text, "expected to find: " + 'Jazz is a distributed database framework for building local-first apps. It syncs data across frontends, serverless functions, and backend servers with real-time collaboration, offline support, and end'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Languages**: TypeScript (primary), Rust (performance-critical CRDT code in `crates/`)' in text, "expected to find: " + '- **Languages**: TypeScript (primary), Rust (performance-critical CRDT code in `crates/`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. Create a changeset using the related skill if the change affects package versions' in text, "expected to find: " + '3. Create a changeset using the related skill if the change affects package versions'[:80]

