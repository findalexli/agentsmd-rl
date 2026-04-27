"""Behavioral checks for claude-code-plugins-plus-skills-featnotionpack-build-skill-1 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md')
    assert 'The Notion API is **free with every workspace plan** — there is no per-call pricing. The real "cost" is the **3 requests/second rate limit** (per integration token) and engineering time wasted on inef' in text, "expected to find: " + 'The Notion API is **free with every workspace plan** — there is no per-call pricing. The real "cost" is the **3 requests/second rate limit** (per integration token) and engineering time wasted on inef'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md')
    assert '**Target:** identify which operations consume > 50% of your request budget. Common culprits are polling loops, page retrieves that duplicate database query data, and unfiltered full-table scans.' in text, "expected to find: " + '**Target:** identify which operations consume > 50% of your request budget. Common culprits are polling loops, page retrieves that duplicate database query data, and unfiltered full-table scans.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md')
    assert '**Pattern A: Stop retrieving pages you already have from database queries.** Database query results include all properties — a separate `pages.retrieve` is redundant unless you need blocks.' in text, "expected to find: " + '**Pattern A: Stop retrieving pages you already have from database queries.** Database query results include all properties — a separate `pages.retrieve` is redundant unless you need blocks.'[:80]

