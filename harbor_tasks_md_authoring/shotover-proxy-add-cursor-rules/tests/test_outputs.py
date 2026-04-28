"""Behavioral checks for shotover-proxy-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shotover-proxy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.md')
    assert 'Shotover is configured by a topology.yaml file which sets up a Source which listens for incoming connections, and a series of transforms which inspect and alter requests before finally sending them of' in text, "expected to find: " + 'Shotover is configured by a topology.yaml file which sets up a Source which listens for incoming connections, and a series of transforms which inspect and alter requests before finally sending them of'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.md')
    assert '+ a static site generator for the https://shotover.io website, includes promotional material and generates the includes the docs for past and present versions of shotover.' in text, "expected to find: " + '+ a static site generator for the https://shotover.io website, includes promotional material and generates the includes the docs for past and present versions of shotover.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/rules.md')
    assert '+ to resolve clippy failures run `cargo clippy --all-targets --features alpha-transforms --fix`, then manually fix any issues not covered by `--fix`' in text, "expected to find: " + '+ to resolve clippy failures run `cargo clippy --all-targets --features alpha-transforms --fix`, then manually fix any issues not covered by `--fix`'[:80]

