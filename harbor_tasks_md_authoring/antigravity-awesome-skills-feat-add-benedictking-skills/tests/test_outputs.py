"""Behavioral checks for antigravity-awesome-skills-feat-add-benedictking-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codex-review/SKILL.md')
    assert 'description: Professional code review with auto CHANGELOG generation, integrated with Codex AI' in text, "expected to find: " + 'description: Professional code review with auto CHANGELOG generation, integrated with Codex AI'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codex-review/SKILL.md')
    assert 'See [GitHub Repository](https://github.com/BenedictKing/codex-review) for examples.' in text, "expected to find: " + 'See [GitHub Repository](https://github.com/BenedictKing/codex-review) for examples.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/codex-review/SKILL.md')
    assert 'Professional code review with auto CHANGELOG generation, integrated with Codex AI' in text, "expected to find: " + 'Professional code review with auto CHANGELOG generation, integrated with Codex AI'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context7-auto-research/SKILL.md')
    assert 'description: Automatically fetch latest library/framework documentation for Claude Code via Context7 API' in text, "expected to find: " + 'description: Automatically fetch latest library/framework documentation for Claude Code via Context7 API'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context7-auto-research/SKILL.md')
    assert 'See [GitHub Repository](https://github.com/BenedictKing/context7-auto-research) for examples.' in text, "expected to find: " + 'See [GitHub Repository](https://github.com/BenedictKing/context7-auto-research) for examples.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context7-auto-research/SKILL.md')
    assert 'Automatically fetch latest library/framework documentation for Claude Code via Context7 API' in text, "expected to find: " + 'Automatically fetch latest library/framework documentation for Claude Code via Context7 API'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/exa-search/SKILL.md')
    assert 'description: Semantic search, similar content discovery, and structured research using Exa API' in text, "expected to find: " + 'description: Semantic search, similar content discovery, and structured research using Exa API'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/exa-search/SKILL.md')
    assert 'Semantic search, similar content discovery, and structured research using Exa API' in text, "expected to find: " + 'Semantic search, similar content discovery, and structured research using Exa API'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/exa-search/SKILL.md')
    assert 'See [GitHub Repository](https://github.com/BenedictKing/exa-search) for examples.' in text, "expected to find: " + 'See [GitHub Repository](https://github.com/BenedictKing/exa-search) for examples.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-scraper/SKILL.md')
    assert 'description: Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API' in text, "expected to find: " + 'description: Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-scraper/SKILL.md')
    assert 'See [GitHub Repository](https://github.com/BenedictKing/firecrawl-scraper) for examples.' in text, "expected to find: " + 'See [GitHub Repository](https://github.com/BenedictKing/firecrawl-scraper) for examples.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/firecrawl-scraper/SKILL.md')
    assert 'Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API' in text, "expected to find: " + 'Deep web scraping, screenshots, PDF parsing, and website crawling using Firecrawl API'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tavily-web/SKILL.md')
    assert 'description: Web search, content extraction, crawling, and research capabilities using Tavily API' in text, "expected to find: " + 'description: Web search, content extraction, crawling, and research capabilities using Tavily API'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tavily-web/SKILL.md')
    assert 'Web search, content extraction, crawling, and research capabilities using Tavily API' in text, "expected to find: " + 'Web search, content extraction, crawling, and research capabilities using Tavily API'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/tavily-web/SKILL.md')
    assert 'See [GitHub Repository](https://github.com/BenedictKing/tavily-web) for examples.' in text, "expected to find: " + 'See [GitHub Repository](https://github.com/BenedictKing/tavily-web) for examples.'[:80]

