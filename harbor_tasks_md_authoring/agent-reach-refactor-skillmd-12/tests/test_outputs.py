"""Behavioral checks for agent-reach-refactor-skillmd-12 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-reach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agent-reach/SKILL.md')
    assert 'agent-reach/SKILL.md' in text, "expected to find: " + 'agent-reach/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/integrations/skill/SKILL.md')
    assert 'agent_reach/integrations/skill/SKILL.md' in text, "expected to find: " + 'agent_reach/integrations/skill/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert '- **Paste cookies:** User installs [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension → goes to the website → exports Header Stri' in text, "expected to find: " + '- **Paste cookies:** User installs [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension → goes to the website → exports Header Stri'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert "`install` auto-detects your environment and installs core dependencies (Node.js, mcporter, bird CLI, gh CLI, instaloader). Read the output and run `agent-reach doctor` to see what's active." in text, "expected to find: " + "`install` auto-detects your environment and installs core dependencies (Node.js, mcporter, bird CLI, gh CLI, instaloader). Read the output and run `agent-reach doctor` to see what's active."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'Handles: tweets, Reddit posts, articles, YouTube/Bilibili (transcripts), GitHub repos, Instagram posts, LinkedIn profiles, Boss直聘 jobs, XiaoHongShu notes, RSS feeds, and any web page.' in text, "expected to find: " + 'Handles: tweets, Reddit posts, articles, YouTube/Bilibili (transcripts), GitHub repos, Instagram posts, LinkedIn profiles, Boss直聘 jobs, XiaoHongShu notes, RSS feeds, and any web page.'[:80]

