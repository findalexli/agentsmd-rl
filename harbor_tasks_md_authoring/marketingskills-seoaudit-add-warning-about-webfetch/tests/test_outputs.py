"""Behavioral checks for marketingskills-seoaudit-add-warning-about-webfetch (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/marketingskills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert '> **Note on schema detection:** `web_fetch` strips `<script>` tags (including JSON-LD) and cannot detect JS-injected schema. Always use the browser tool, Rich Results Test, or Screaming Frog for schem' in text, "expected to find: " + '> **Note on schema detection:** `web_fetch` strips `<script>` tags (including JSON-LD) and cannot detect JS-injected schema. Always use the browser tool, Rich Results Test, or Screaming Frog for schem'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert "Many CMS plugins (AIOSEO, Yoast, RankMath) inject JSON-LD via client-side JavaScript — it won't appear in static HTML or `web_fetch` output (which strips `<script>` tags during conversion)." in text, "expected to find: " + "Many CMS plugins (AIOSEO, Yoast, RankMath) inject JSON-LD via client-side JavaScript — it won't appear in static HTML or `web_fetch` output (which strips `<script>` tags during conversion)."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seo-audit/SKILL.md')
    assert '**Never report "no schema found" based solely on `web_fetch` or `curl`.** This has led to false audit findings in production.' in text, "expected to find: " + '**Never report "no schema found" based solely on `web_fetch` or `curl`.** This has led to false audit findings in production.'[:80]

