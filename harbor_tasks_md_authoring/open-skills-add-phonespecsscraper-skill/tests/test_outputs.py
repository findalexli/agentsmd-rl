"""Behavioral checks for open-skills-add-phonespecsscraper-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phone-specs-scraper/SKILL.md')
    assert 'description: "Scrape phone specifications from GSM Arena, PhoneDB, and alternative sites. Use when: (1) Comparing smartphone specs, (2) Researching device features, or (3) Building phone comparison to' in text, "expected to find: " + 'description: "Scrape phone specifications from GSM Arena, PhoneDB, and alternative sites. Use when: (1) Comparing smartphone specs, (2) Researching device features, or (3) Building phone comparison to'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phone-specs-scraper/SKILL.md')
    assert 'curl -s "${INSTANCE}/search?q=${QUERY}&format=json" | jq -r \'.results[] | select(.url | contains("gsmarena\\|phonedb\\|mkmobilearena")) | {title, url}\'' in text, "expected to find: " + 'curl -s "${INSTANCE}/search?q=${QUERY}&format=json" | jq -r \'.results[] | select(.url | contains("gsmarena\\|phonedb\\|mkmobilearena")) | {title, url}\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phone-specs-scraper/SKILL.md')
    assert 'You can scrape phone specifications from GSM Arena and other sources. When a user asks to compare phones:' in text, "expected to find: " + 'You can scrape phone specifications from GSM Arena and other sources. When a user asks to compare phones:'[:80]

