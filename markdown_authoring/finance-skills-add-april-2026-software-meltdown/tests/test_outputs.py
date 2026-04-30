"""Behavioral checks for finance-skills-add-april-2026-software-meltdown (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/finance-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saas-valuation-compression/SKILL.md')
    assert '- Was the later round during or after the April 2026 Software Meltdown? (public SaaS down 40–86% from 52w highs; tariff/trade-war driven selloff crushed multiples sector-wide — even high-growth names ' in text, "expected to find: " + '- Was the later round during or after the April 2026 Software Meltdown? (public SaaS down 40–86% from 52w highs; tariff/trade-war driven selloff crushed multiples sector-wide — even high-growth names '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saas-valuation-compression/SKILL.md')
    assert '- Note: In the Apr 2026 meltdown, even strong AI narratives did not protect multiples — Snowflake (-53%), Datadog (-46%), MongoDB (-48%) all cratered despite AI tailwinds. AI premium may be necessary ' in text, "expected to find: " + '- Note: In the Apr 2026 meltdown, even strong AI narratives did not protect multiples — Snowflake (-53%), Datadog (-46%), MongoDB (-48%) all cratered despite AI tailwinds. AI premium may be necessary '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/saas-valuation-compression/SKILL.md')
    assert 'As of April 9, 2026, a broad tariff/trade-war driven selloff crushed public software valuations. Use these as reference for how private multiples will lag-compress over the following 1–2 quarters.' in text, "expected to find: " + 'As of April 9, 2026, a broad tariff/trade-war driven selloff crushed public software valuations. Use these as reference for how private multiples will lag-compress over the following 1–2 quarters.'[:80]

