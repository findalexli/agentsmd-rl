"""Behavioral checks for claude-code-plugins-plus-skills-featnotionpack-build-skill-3 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md')
    assert 'Set up a fast, reproducible local development workflow for Notion integrations. This skill covers creating a dedicated dev integration with its own token, structuring the project for testability, mock' in text, "expected to find: " + 'Set up a fast, reproducible local development workflow for Notion integrations. This skill covers creating a dedicated dev integration with its own token, structuring the project for testability, mock'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md')
    assert '**Unit tests** mock the entire `@notionhq/client` module so they run instantly with no network calls. **Integration tests** hit the real API but are gated behind an environment variable and target onl' in text, "expected to find: " + '**Unit tests** mock the entire `@notionhq/client` module so they run instantly with no network calls. **Integration tests** hit the real API but are gated behind an environment variable and target onl'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md')
    assert '| `404 Not found` (database/page) | Test DB not shared with dev integration | Open DB in Notion > `...` > Connections > add your dev integration |' in text, "expected to find: " + '| `404 Not found` (database/page) | Test DB not shared with dev integration | Open DB in Notion > `...` > Connections > add your dev integration |'[:80]

