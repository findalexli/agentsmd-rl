"""Behavioral checks for awesome-solidity-docs-add-agentsmd-with-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-solidity")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Run that command locally before committing when adding/changing links — a single dead URL fails the build. `awesome_bot` occasionally flags transient 4xx/5xx from rate limiting; re-running usually cle' in text, "expected to find: " + 'Run that command locally before committing when adding/changing links — a single dead URL fails the build. `awesome_bot` occasionally flags transient 4xx/5xx from rate limiting; re-running usually cle'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`awesome-solidity` is a curated "awesome list" of Solidity resources, libraries, and tools. The entire content of the list lives in a single file: `README.md`. There is no application code — PRs almos' in text, "expected to find: " + '`awesome-solidity` is a curated "awesome list" of Solidity resources, libraries, and tools. The entire content of the list lives in a single file: `README.md`. There is no application code — PRs almos'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The repo is served as a GitHub Pages Jekyll site (`_config.yml` sets `theme: jekyll-theme-cayman`). The default branch is `gh-pages` (not `main`/`master`); open PRs against `gh-pages`.' in text, "expected to find: " + 'The repo is served as a GitHub Pages Jekyll site (`_config.yml` sets `theme: jekyll-theme-cayman`). The default branch is `gh-pages` (not `main`/`master`); open PRs against `gh-pages`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

