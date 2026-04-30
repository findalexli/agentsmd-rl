"""Behavioral checks for liveblog-add-agentsmd-and-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/liveblog")


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
    assert '- **Comment-based storage**: Liveblog entries are stored as WordPress comments, not custom post types or tables. The `CommentEntryRepository` implements `EntryRepositoryInterface`. Do not switch to cu' in text, "expected to find: " + '- **Comment-based storage**: Liveblog entries are stored as WordPress comments, not custom post types or tables. The `CommentEntryRepository` implements `EntryRepositoryInterface`. Do not switch to cu'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Content filter pipeline**: Content filters (Author, Hashtag, Emoji, Command) are registered via `ContentFilterRegistry`. Extend this registry for new filters rather than adding ad-hoc processing.' in text, "expected to find: " + '- **Content filter pipeline**: Content filters (Author, Hashtag, Emoji, Command) are registered via `ContentFilterRegistry`. Extend this registry for new filters rather than adding ad-hoc processing.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Domain-Driven Design (DDD)**: Clear separation into Domain, Application, and Infrastructure layers. New code must respect these boundaries — domain classes must not depend on WordPress.' in text, "expected to find: " + '- **Domain-Driven Design (DDD)**: Clear separation into Domain, Application, and Infrastructure layers. New code must respect these boundaries — domain classes must not depend on WordPress.'[:80]

