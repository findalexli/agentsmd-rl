"""Behavioral checks for herbie-update-agentsmd-a-bit (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/herbie")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- You can enable the `egglog` backend with `--enable generate:egglog`.' in text, "expected to find: " + '- You can enable the `egglog` backend with `--enable generate:egglog`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Documentation lives in `www/doc/2.3/` and is HTML-formatted. Update' in text, "expected to find: " + '- Documentation lives in `www/doc/2.3/` and is HTML-formatted. Update'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- You can pass `--timeout T` to time out a benchmark after T seconds.' in text, "expected to find: " + '- You can pass `--timeout T` to time out a benchmark after T seconds.'[:80]

