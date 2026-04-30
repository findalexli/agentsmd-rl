"""Behavioral checks for claude-code-marketing-skills-featuresolo-tier-launch (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-marketing-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cogny/SKILL.md')
    assert '3. Use `update_finding` to merge duplicate findings into one (update the body to combine details, then delete the duplicates)' in text, "expected to find: " + '3. Use `update_finding` to merge duplicate findings into one (update the body to combine details, then delete the duplicates)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cogny/SKILL.md')
    assert 'When you discover important, reusable insights about the business (not one-off findings), save them to the context tree:' in text, "expected to find: " + 'When you discover important, reusable insights about the business (not one-off findings), save them to the context tree:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/cogny/SKILL.md')
    assert '- `write_context_node` with path like `insights/seo/top-keywords` or `insights/linkedin/audience-profile`' in text, "expected to find: " + '- `write_context_node` with path like `insights/seo/top-keywords` or `insights/linkedin/audience-profile`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/linkedin-ads-audit/SKILL.md')
    assert '"body": "Campaign targeting C-suite titles with single image ads. CPC is 55% above LinkedIn average. Recommend: 1) Test carousel format 2) Narrow to VP+ titles only 3) Add company size >500 filter",' in text, "expected to find: " + '"body": "Campaign targeting C-suite titles with single image ads. CPC is 55% above LinkedIn average. Recommend: 1) Test carousel format 2) Narrow to VP+ titles only 3) Add company size >500 filter",'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/linkedin-ads-audit/SKILL.md')
    assert 'description: Full LinkedIn Ads account audit — campaign structure, targeting, creative performance, spend efficiency' in text, "expected to find: " + 'description: Full LinkedIn Ads account audit — campaign structure, targeting, creative performance, spend efficiency'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/linkedin-ads-audit/SKILL.md')
    assert 'Perform a comprehensive LinkedIn Ads account audit using live data from the connected LinkedIn Ads MCP.' in text, "expected to find: " + 'Perform a comprehensive LinkedIn Ads account audit using live data from the connected LinkedIn Ads MCP.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert '"body": "Pages /pricing, /features, /blog/... lack meta descriptions. Average CTR for pages without descriptions is 30% lower.",' in text, "expected to find: " + '"body": "Pages /pricing, /features, /blog/... lack meta descriptions. Average CTR for pages without descriptions is 30% lower.",'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert 'If the Cogny MCP is connected (`mcp__cogny__create_finding` available), record each actionable finding:' in text, "expected to find: " + 'If the Cogny MCP is connected (`mcp__cogny__create_finding` available), record each actionable finding:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert 'Want live Search Console data (actual queries, rankings, click-through rates, indexing status)?' in text, "expected to find: " + 'Want live Search Console data (actual queries, rankings, click-through rates, indexing status)?'[:80]

