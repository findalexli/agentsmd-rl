"""Behavioral checks for buildwithclaude-add-szamlazzinvoicing-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/szamlazz-invoicing/SKILL.md')
    assert 'description: "Issue, cancel, and fetch Hungarian invoices via the szamlazz.hu Agent API. Handles VAT calculation, NAV taxpayer lookup, partner caching, and PDF generation. Use when the user mentions s' in text, "expected to find: " + 'description: "Issue, cancel, and fetch Hungarian invoices via the szamlazz.hu Agent API. Handles VAT calculation, NAV taxpayer lookup, partner caching, and PDF generation. Use when the user mentions s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/szamlazz-invoicing/SKILL.md')
    assert '2. **Invoice creation** — parses natural language, resolves customer from partner cache or NAV, calculates net/VAT/gross with Decimal precision, shows mandatory confirmation, fires XML to API, saves P' in text, "expected to find: " + '2. **Invoice creation** — parses natural language, resolves customer from partner cache or NAV, calculates net/VAT/gross with Decimal precision, shows mandatory confirmation, fires XML to API, saves P'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/szamlazz-invoicing/SKILL.md')
    assert '1. **First-run setup** — detects missing config, asks 3 questions (API key, seller tax number with NAV auto-lookup, bank account with auto-detection), writes `seller.yaml`' in text, "expected to find: " + '1. **First-run setup** — detects missing config, asks 3 questions (API key, seller tax number with NAV auto-lookup, bank account with auto-detection), writes `seller.yaml`'[:80]

