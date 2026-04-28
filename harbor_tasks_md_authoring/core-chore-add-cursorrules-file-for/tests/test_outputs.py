"""Behavioral checks for core-chore-add-cursorrules-file-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'Calimero is a decentralized infrastructure platform with WebAssembly runtime, peer-to-peer networking, and blockchain integrations. The codebase is primarily Rust with multiple crates organized as a w' in text, "expected to find: " + 'Calimero is a decentralized infrastructure platform with WebAssembly runtime, peer-to-peer networking, and blockchain integrations. The codebase is primarily Rust with multiple crates organized as a w'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- **Primitives crates**: Shared types go in `*-primitives` crates (e.g., `calimero-context-primitives`)' in text, "expected to find: " + '- **Primitives crates**: Shared types go in `*-primitives` crates (e.g., `calimero-context-primitives`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Profile configurations: `dev`, `release`, `app-release`, `profiling`, `app-profiling`' in text, "expected to find: " + '- Profile configurations: `dev`, `release`, `app-release`, `profiling`, `app-profiling`'[:80]

