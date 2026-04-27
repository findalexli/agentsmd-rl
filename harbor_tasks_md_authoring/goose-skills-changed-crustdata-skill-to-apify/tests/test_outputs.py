"""Behavioral checks for goose-skills-changed-crustdata-skill-to-apify (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/champion-tracker/SKILL.md')
    assert '2. **Search LinkedIn posts** — Use the `linkedin-post-research` skill (Apify-based) to find people who posted about the product.' in text, "expected to find: " + '2. **Search LinkedIn posts** — Use the `linkedin-post-research` skill (Apify-based) to find people who posted about the product.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/champion-tracker/SKILL.md')
    assert '3. **Resolve LinkedIn URLs** — Use Fiber `/v1/kitchen-sink/person` (name + company → profile URL) or ContactOut via Orthogonal.' in text, "expected to find: " + '3. **Resolve LinkedIn URLs** — Use Fiber `/v1/kitchen-sink/person` (name + company → profile URL) or ContactOut via Orthogonal.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/capabilities/customer-discovery/SKILL.md')
    assert '- `skills/capabilities/linkedin-post-research/scripts/search_posts.py` — LinkedIn post search (requires Apify token)' in text, "expected to find: " + '- `skills/capabilities/linkedin-post-research/scripts/search_posts.py` — LinkedIn post search (requires Apify token)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/industry-scanner/SKILL.md')
    assert 'Delegate to the `linkedin-post-research` skill (uses the `apimaestro~linkedin-posts-search-scraper-no-cookies` Apify actor). Search each keyword with `date_posted: "past-day"` (or `"past-week"` for we' in text, "expected to find: " + 'Delegate to the `linkedin-post-research` skill (uses the `apimaestro~linkedin-posts-search-scraper-no-cookies` Apify actor). Search each keyword with `date_posted: "past-day"` (or `"past-week"` for we'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/industry-scanner/SKILL.md')
    assert '- `APIFY_API_TOKEN` — LinkedIn post search goes through the `linkedin-post-research` skill (Apify-based)' in text, "expected to find: " + '- `APIFY_API_TOKEN` — LinkedIn post search goes through the `linkedin-post-research` skill (Apify-based)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/industry-scanner/SKILL.md')
    assert 'Read `skills/linkedin-post-research/SKILL.md` for the full Apify workflow.' in text, "expected to find: " + 'Read `skills/linkedin-post-research/SKILL.md` for the full Apify workflow.'[:80]

