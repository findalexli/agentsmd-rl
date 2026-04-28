"""Behavioral checks for indicator-agentsmd-added (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/indicator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Indicator is a Golang library providing technical analysis indicators, strategies, and a backtesting framework. It uses Go 1.22+ with generics and channels for streaming data processing.' in text, "expected to find: " + 'Indicator is a Golang library providing technical analysis indicators, strategies, and a backtesting framework. It uses Go 1.22+ with generics and channels for streaming data processing.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Packages**: Organized by category (trend, momentum, volatility, volume, strategy, helper, etc.)' in text, "expected to find: " + '- **Packages**: Organized by category (trend, momentum, volatility, volume, strategy, helper, etc.)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Test files**: Named `*_test.go` in same package with `_test` suffix (e.g., `apo_test.go`)' in text, "expected to find: " + '- **Test files**: Named `*_test.go` in same package with `_test` suffix (e.g., `apo_test.go`)'[:80]

