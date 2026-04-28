"""Behavioral checks for workers-sdk-docs-add-agentsmd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workers-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the **Cloudflare Workers SDK** monorepo containing tools and libraries for developing, testing, and deploying applications on Cloudflare. The main components are Wrangler (CLI), Miniflare (loc' in text, "expected to find: " + 'This is the **Cloudflare Workers SDK** monorepo containing tools and libraries for developing, testing, and deploying applications on Cloudflare. The main components are Wrangler (CLI), Miniflare (loc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Every change to package code requires a changeset or it will not trigger a release. Read `.changeset/README.md` before creating changesets.' in text, "expected to find: " + 'Every change to package code requires a changeset or it will not trigger a release. Read `.changeset/README.md` before creating changesets.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PR template requirements: Remove "Fixes #..." line when no relevant issue exists, keep all checkboxes (don\'t delete unchecked ones)' in text, "expected to find: " + '- PR template requirements: Remove "Fixes #..." line when no relevant issue exists, keep all checkboxes (don\'t delete unchecked ones)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See @AGENTS.md' in text, "expected to find: " + 'See @AGENTS.md'[:80]

