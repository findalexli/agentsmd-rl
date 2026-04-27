"""Behavioral checks for prometheus-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prometheus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Each commit must compile and pass tests independently, except when one commit adds a test to expose a bug and then the next commit fixes the bug.' in text, "expected to find: " + '- Each commit must compile and pass tests independently, except when one commit adds a test to expose a bug and then the next commit fixes the bug.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '[Go: Best Practices for Production Environments](https://peter.bourgon.org/go-in-production/#formatting-and-style).' in text, "expected to find: " + '[Go: Best Practices for Production Environments](https://peter.bourgon.org/go-in-production/#formatting-and-style).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run benchmarks before and after the change using `go test -count=6 -benchmem -bench <directory changed in PR>`' in text, "expected to find: " + '- Run benchmarks before and after the change using `go test -count=6 -benchmem -bench <directory changed in PR>`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

