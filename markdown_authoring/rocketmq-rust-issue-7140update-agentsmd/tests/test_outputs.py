"""Behavioral checks for rocketmq-rust-issue-7140update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rocketmq-rust")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Root workspace commands do not cover standalone projects. If changes affect one of these projects, validate it in its own directory and follow any deeper `AGENTS.md` there:' in text, "expected to find: " + 'Root workspace commands do not cover standalone projects. If changes affect one of these projects, validate it in its own directory and follow any deeper `AGENTS.md` there:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Documentation-only changes do not require Cargo validation unless they affect generated Rust, build configuration, examples, or documented commands that need verification.' in text, "expected to find: " + 'Documentation-only changes do not require Cargo validation unless they affect generated Rust, build configuration, examples, or documented commands that need verification.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use patch-style edits for manual changes when tool support is available. Generated files and formatter output may be produced by their normal tools.' in text, "expected to find: " + '- Use patch-style edits for manual changes when tool support is available. Generated files and formatter output may be produced by their normal tools.'[:80]

