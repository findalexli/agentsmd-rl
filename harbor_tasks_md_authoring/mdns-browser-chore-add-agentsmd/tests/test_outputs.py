"""Behavioral checks for mdns-browser-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mdns-browser")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document contains guidelines and commands for agentic coding agents working on the mdns-browser repository.' in text, "expected to find: " + 'This document contains guidelines and commands for agentic coding agents working on the mdns-browser repository.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- All structs crossing the frontend-backend boundary need `#[derive(Serialize, Deserialize)]`' in text, "expected to find: " + '- All structs crossing the frontend-backend boundary need `#[derive(Serialize, Deserialize)]`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow Rust naming conventions (snake_case for functions, PascalCase for types)' in text, "expected to find: " + '- Follow Rust naming conventions (snake_case for functions, PascalCase for types)'[:80]

