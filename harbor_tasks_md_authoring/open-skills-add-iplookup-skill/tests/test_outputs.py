"""Behavioral checks for open-skills-add-iplookup-skill (markdown_authoring task).

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
    text = _read('skills/ip-lookup/SKILL.md')
    assert '"Use the ip-lookup skill to query at least four public IP information providers for {ip}. Return a short JSON summary: best_match (country/city), score, and per-source details (country, region, city, ' in text, "expected to find: " + '"Use the ip-lookup skill to query at least four public IP information providers for {ip}. Return a short JSON summary: best_match (country/city), score, and per-source details (country, region, city, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ip-lookup/SKILL.md')
    assert 'try { const res = await fetch(url, {signal: controller.signal}); clearTimeout(id); if(!res.ok) throw new Error(res.statusText); return await res.json(); } catch(e){ clearTimeout(id); throw e; }' in text, "expected to find: " + 'try { const res = await fetch(url, {signal: controller.signal}); clearTimeout(id); if(!res.ok) throw new Error(res.statusText); return await res.json(); } catch(e){ clearTimeout(id); throw e; }'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ip-lookup/SKILL.md')
    assert '- Query multiple public IP information providers and aggregate results to produce a concise, best-match location and metadata summary for an IP address.' in text, "expected to find: " + '- Query multiple public IP information providers and aggregate results to produce a concise, best-match location and metadata summary for an IP address.'[:80]

