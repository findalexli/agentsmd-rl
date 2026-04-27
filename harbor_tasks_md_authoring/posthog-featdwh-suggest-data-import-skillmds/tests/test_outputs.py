"""Behavioral checks for posthog-featdwh-suggest-data-import-skillmds (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('products/data_warehouse/skills/suggesting-data-imports/SKILL.md')
    assert "description: 'Use when the user asks about revenue, payments, subscriptions, billing, CRM deals, support tickets, production database tables, or other data that PostHog does not collect natively. Also" in text, "expected to find: " + "description: 'Use when the user asks about revenue, payments, subscriptions, billing, CRM deals, support tickets, production database tables, or other data that PostHog does not collect natively. Also"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('products/data_warehouse/skills/suggesting-data-imports/SKILL.md')
    assert 'PostHog collects product analytics events, persons, sessions, and groups via its SDKs. Additional products are available but must be enabled: session replay, feature flags, experiments, surveys, web a' in text, "expected to find: " + 'PostHog collects product analytics events, persons, sessions, and groups via its SDKs. Additional products are available but must be enabled: session replay, feature flags, experiments, surveys, web a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('products/data_warehouse/skills/suggesting-data-imports/SKILL.md')
    assert 'Example: "Your Stripe data isn\'t in PostHog yet. If you connect a Stripe source, you\'ll get tables like `charges`, `subscriptions`, and `customers` that you can join with PostHog events to analyze rev' in text, "expected to find: " + 'Example: "Your Stripe data isn\'t in PostHog yet. If you connect a Stripe source, you\'ll get tables like `charges`, `subscriptions`, and `customers` that you can join with PostHog events to analyze rev'[:80]

