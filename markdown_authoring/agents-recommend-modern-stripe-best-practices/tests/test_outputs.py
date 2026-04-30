"""Behavioral checks for agents-recommend-modern-stripe-best-practices (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/payment-processing/skills/stripe-integration/SKILL.md')
    assert '- Provides built-in checkout capabilities (line items, discounts, tax, shipping, address collection, saved payment methods, and checkout lifecycle events)' in text, "expected to find: " + '- Provides built-in checkout capabilities (line items, discounts, tax, shipping, address collection, saved payment methods, and checkout lifecycle events)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/payment-processing/skills/stripe-integration/SKILL.md')
    assert "Pattern 2 (Elements with Checkout Sessions) is Stripe's recommended approach, but you can also use Payment Intents as an alternative." in text, "expected to find: " + "Pattern 2 (Elements with Checkout Sessions) is Stripe's recommended approach, but you can also use Payment Intents as an alternative."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/payment-processing/skills/stripe-integration/SKILL.md')
    assert '- You calculate the final amount with taxes, discounts, subscriptions, and currency conversion yourself.' in text, "expected to find: " + '- You calculate the final amount with taxes, discounts, subscriptions, and currency conversion yourself.'[:80]

