"""Behavioral checks for obsidian-wiki-fix-harden-wikiingest-against-prompt (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-wiki")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '**Deletion safety:** Only delete the specific file that was just promoted. Before deleting, verify the resolved path is inside `$OBSIDIAN_VAULT_PATH/_raw/` — never delete files outside this directory.' in text, "expected to find: " + '**Deletion safety:** Only delete the specific file that was just promoted. Before deleting, verify the resolved path is inside `$OBSIDIAN_VAULT_PATH/_raw/` — never delete files outside this directory.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '- Compute the file\'s SHA-256 hash: `sha256sum -- "<file>"` (or `shasum -a 256 -- "<file>"` on macOS). Always double-quote the path and use `--` to prevent filenames with special characters or leading ' in text, "expected to find: " + '- Compute the file\'s SHA-256 hash: `sha256sum -- "<file>"` (or `shasum -a 256 -- "<file>"` on macOS). Always double-quote the path and use `--` to prevent filenames with special characters or leading '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.skills/wiki-ingest/SKILL.md')
    assert '1. Read `~/.obsidian-wiki/config` (preferred) or `.env` (fallback) to get `OBSIDIAN_VAULT_PATH` and `OBSIDIAN_SOURCES_DIR`. Only read the specific variables you need — do not log, echo, or reference a' in text, "expected to find: " + '1. Read `~/.obsidian-wiki/config` (preferred) or `.env` (fallback) to get `OBSIDIAN_VAULT_PATH` and `OBSIDIAN_SOURCES_DIR`. Only read the specific variables you need — do not log, echo, or reference a'[:80]

