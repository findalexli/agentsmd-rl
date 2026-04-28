"""Behavioral checks for co-authors-plus-add-agentsmd-and-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/co-authors-plus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '.claude/CLAUDE.md' in text, "expected to find: " + '.claude/CLAUDE.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Taxonomy-based storage**: Coauthor relationships are stored via the `author` taxonomy, with term slugs in the format `cap-{user_nicename}`. This leverages WordPress's taxonomy infrastructure for q" in text, "expected to find: " + "- **Taxonomy-based storage**: Coauthor relationships are stored via the `author` taxonomy, with term slugs in the format `cap-{user_nicename}`. This leverages WordPress's taxonomy infrastructure for q"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Template tags are public API**: Functions in `template-tags.php` (`coauthors()`, `get_coauthors()`, `coauthors_posts_links()`, etc.) are used by themes in production. Do not rename, remove, or cha' in text, "expected to find: " + '- **Template tags are public API**: Functions in `template-tags.php` (`coauthors()`, `get_coauthors()`, `coauthors_posts_links()`, etc.) are used by themes in production. Do not rename, remove, or cha'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Post author field sync**: The plugin syncs `wp_posts.post_author` via the `coauthors_set_post_author_field` filter to maintain backward compatibility with queries expecting a single author. Do not' in text, "expected to find: " + '- **Post author field sync**: The plugin syncs `wp_posts.post_author` via the `coauthors_set_post_author_field` filter to maintain backward compatibility with queries expecting a single author. Do not'[:80]

