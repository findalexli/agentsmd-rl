"""Behavioral checks for marketingskills-feat-add-pricingmd-guidance-to (markdown_authoring task).

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
    text = _read('skills/ai-seo/SKILL.md')
    assert "AI agents aren't just answering questions — they're becoming buyers. When an AI agent evaluates tools on behalf of a user, it needs structured, parseable information. If your pricing is locked in a Ja" in text, "expected to find: " + "AI agents aren't just answering questions — they're becoming buyers. When an AI agent evaluates tools on behalf of a user, it needs structured, parseable information. If your pricing is locked in a Ja"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-seo/SKILL.md')
    assert '- Pricing transparency (AI cites pages with visible pricing) — add a `/pricing.md` file so AI agents can parse your plans without rendering your page (see "Machine-Readable Files" above)' in text, "expected to find: " + '- Pricing transparency (AI cites pages with visible pricing) — add a `/pricing.md` file so AI agents can parse your plans without rendering your page (see "Machine-Readable Files" above)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ai-seo/SKILL.md')
    assert '- **Hiding pricing behind "contact sales" or JS-rendered pages** — AI agents evaluating your product on behalf of buyers can\'t parse what they can\'t read. Add a `/pricing.md` file' in text, "expected to find: " + '- **Hiding pricing behind "contact sales" or JS-rendered pages** — AI agents evaluating your product on behalf of buyers can\'t parse what they can\'t read. Add a `/pricing.md` file'[:80]

