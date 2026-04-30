"""Behavioral checks for debbie.codes-improve-addcontent-skill-better-triggers (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/debbie.codes")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert 'debbie.codes website. Triggered by phrases like: "add video", "add blog", "add blog post",' in text, "expected to find: " + 'debbie.codes website. Triggered by phrases like: "add video", "add blog", "add blog post",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert '"add podcast", "add this video", "add this to the site", or any request with a YouTube,' in text, "expected to find: " + '"add podcast", "add this video", "add this to the site", or any request with a YouTube,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/SKILL.md')
    assert 'podcast, or blog URL to be added as content. Handles browser-based metadata extraction' in text, "expected to find: " + 'podcast, or blog URL to be added as content. Handles browser-based metadata extraction'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/blog.md')
    assert 'playwright-cli open "<blog-url>"' in text, "expected to find: " + 'playwright-cli open "<blog-url>"'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'First, kill any existing dev server on port 3001:' in text, "expected to find: " + 'First, kill any existing dev server on port 3001:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'kill $(lsof -ti:3001) 2>/dev/null' in text, "expected to find: " + 'kill $(lsof -ti:3001) 2>/dev/null'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/environment.md')
    assert 'Then install and start:' in text, "expected to find: " + 'Then install and start:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert 'description: Discover how to perform manual testing using Playwright MCP without writing any code, using simple prompts instead. This revolutionary approach makes testing accessible to everyone, regar' in text, "expected to find: " + 'description: Discover how to perform manual testing using Playwright MCP without writing any code, using simple prompts instead. This revolutionary approach makes testing accessible to everyone, regar'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert '**File**: `content/videos/manual-testing-with-playwright-mcp-no-code-just-prompts.md`' in text, "expected to find: " + '**File**: `content/videos/manual-testing-with-playwright-mcp-no-code-just-prompts.md`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-content/references/video.md')
    assert 'title: Manual Testing with Playwright MCP – No Code, Just Prompts!' in text, "expected to find: " + 'title: Manual Testing with Playwright MCP – No Code, Just Prompts!'[:80]

