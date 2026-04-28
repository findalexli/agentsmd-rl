"""Behavioral checks for cli-update-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/SKILL.md')
    assert 'Unless the user specifies to return in context, write results to `.firecrawl/` with `-o`. Add `.firecrawl/` to `.gitignore`. Always quote URLs - shell interprets `?` and `&` as special characters.' in text, "expected to find: " + 'Unless the user specifies to return in context, write results to `.firecrawl/` with `-o`. Add `.firecrawl/` to `.gitignore`. Always quote URLs - shell interprets `?` and `&` as special characters.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/SKILL.md')
    assert '5. **Browser** - Scrape failed because content is behind interaction (pagination, modals, form submissions, multi-step navigation).' in text, "expected to find: " + '5. **Browser** - Scrape failed because content is behind interaction (pagination, modals, form submissions, multi-step navigation).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/SKILL.md')
    assert 'Official Firecrawl CLI skill for web scraping, search, crawling, and browser automation. Returns clean LLM-optimized markdown.' in text, "expected to find: " + 'Official Firecrawl CLI skill for web scraping, search, crawling, and browser automation. Returns clean LLM-optimized markdown.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/install.md')
    assert 'Install the official Firecrawl CLI and handle authentication.' in text, "expected to find: " + 'Install the official Firecrawl CLI and handle authentication.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/install.md')
    assert 'Package: https://www.npmjs.com/package/firecrawl-cli' in text, "expected to find: " + 'Package: https://www.npmjs.com/package/firecrawl-cli'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/install.md')
    assert 'Docs: https://docs.firecrawl.dev/sdks/cli' in text, "expected to find: " + 'Docs: https://docs.firecrawl.dev/sdks/cli'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/security.md')
    assert 'Security guidelines for handling web content fetched by the official Firecrawl CLI.' in text, "expected to find: " + 'Security guidelines for handling web content fetched by the official Firecrawl CLI.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/security.md')
    assert 'Package: https://www.npmjs.com/package/firecrawl-cli' in text, "expected to find: " + 'Package: https://www.npmjs.com/package/firecrawl-cli'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-cli/rules/security.md')
    assert 'Docs: https://docs.firecrawl.dev/sdks/cli' in text, "expected to find: " + 'Docs: https://docs.firecrawl.dev/sdks/cli'[:80]

