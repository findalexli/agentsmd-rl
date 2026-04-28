"""Behavioral checks for docs-feat-custom-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert '**Triggers**: `swap`, `quote`, `gasless`, `best route`, `lend`, `borrow`, `earn`, `liquidation`, `perps`, `leverage`, `long`, `short`, `position`, `limit order`, `trigger`, `price condition`, `dca`, `' in text, "expected to find: " + '**Triggers**: `swap`, `quote`, `gasless`, `best route`, `lend`, `borrow`, `earn`, `liquidation`, `perps`, `leverage`, `long`, `short`, `position`, `limit order`, `trigger`, `price condition`, `dca`, `'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert '- **DEX Integration** (into Iris): Free, no fees. Prereqs: code health, security audit, market traction. Implement `jupiter-amm-interface` crate. **Critical**: No network calls in implementation (acco' in text, "expected to find: " + '- **DEX Integration** (into Iris): Free, no fees. Prereqs: code health, security audit, market traction. Implement `jupiter-amm-interface` crate. **Critical**: No network calls in implementation (acco'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert '- Refs: [Overview](https://dev.jup.ag/docs/recurring/index.md) | [Create](https://dev.jup.ag/docs/recurring/create-order.md) | [Get orders](https://dev.jup.ag/docs/recurring/get-recurring-orders.md) |' in text, "expected to find: " + '- Refs: [Overview](https://dev.jup.ag/docs/recurring/index.md) | [Create](https://dev.jup.ag/docs/recurring/create-order.md) | [Get orders](https://dev.jup.ag/docs/recurring/get-recurring-orders.md) |'[:80]

