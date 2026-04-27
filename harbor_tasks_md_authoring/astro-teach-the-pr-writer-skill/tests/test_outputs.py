"""Behavioral checks for astro-teach-the-pr-writer-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/astro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/astro-pr-writer/SKILL.md')
    assert '**New features (minor)** — start with "Adds", name the new API, and describe what users can now do. Include a code example when helpful. New features are also an opportunity to write a richer descript' in text, "expected to find: " + '**New features (minor)** — start with "Adds", name the new API, and describe what users can now do. Include a code example when helpful. New features are also an opportunity to write a richer descript'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/astro-pr-writer/SKILL.md')
    assert 'Create `.changeset/<descriptive-slug>.md` with YAML front matter listing affected packages and bump type, followed by a plain-text description that becomes the changelog entry:' in text, "expected to find: " + 'Create `.changeset/<descriptive-slug>.md` with YAML front matter listing affected packages and bump type, followed by a plain-text description that becomes the changelog entry:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/astro-pr-writer/SKILL.md')
    assert '**Breaking changes (major)** — use verbs like "Removes", "Changes", or "Deprecates". Must include migration guidance; use diff code samples when appropriate:' in text, "expected to find: " + '**Breaking changes (major)** — use verbs like "Removes", "Changes", or "Deprecates". Must include migration guidance; use diff code samples when appropriate:'[:80]

