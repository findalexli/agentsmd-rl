"""Behavioral checks for vitess-claudemd-required-code-is-formatted (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [ ] Golang code passes the `goimports -local "vitess.io/vitess" -w ...` formatter' in text, "expected to find: " + '- [ ] Golang code passes the `goimports -local "vitess.io/vitess" -w ...` formatter'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Always sign git commits with the `git commit --signoff` flag' in text, "expected to find: " + '- Always sign git commits with the `git commit --signoff` flag'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [ ] Golang code passes the `gofumpt` formatter' in text, "expected to find: " + '- [ ] Golang code passes the `gofumpt` formatter'[:80]

