"""Behavioral checks for open-skills-add-usingscrapy-skill (markdown_authoring task).

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
    text = _read('skills/using-scrapy/SKILL.md')
    assert 'description: "Scrape websites at scale using Scrapy, a Python web crawling and scraping framework. Use when: (1) Crawling multiple pages or entire sites, (2) Extracting structured data from HTML/XML, ' in text, "expected to find: " + 'description: "Scrape websites at scale using Scrapy, a Python web crawling and scraping framework. Use when: (1) Crawling multiple pages or entire sites, (2) Extracting structured data from HTML/XML, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/using-scrapy/SKILL.md')
    assert 'Scrapy is a fast, high-level Python web crawling and scraping framework. It enables structured data extraction from websites, supports crawling entire sites, and integrates pipelines to process and st' in text, "expected to find: " + 'Scrapy is a fast, high-level Python web crawling and scraping framework. It enables structured data extraction from websites, supports crawling entire sites, and integrates pipelines to process and st'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/using-scrapy/SKILL.md')
    assert "- Solution: Review the site's robots.txt; only scrape paths that are allowed, or set `ROBOTSTXT_OBEY = False` if you have explicit permission from the site owner" in text, "expected to find: " + "- Solution: Review the site's robots.txt; only scrape paths that are allowed, or set `ROBOTSTXT_OBEY = False` if you have explicit permission from the site owner"[:80]

