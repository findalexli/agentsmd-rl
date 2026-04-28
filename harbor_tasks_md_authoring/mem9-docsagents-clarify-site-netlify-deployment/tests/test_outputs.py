"""Behavioral checks for mem9-docsagents-clarify-site-netlify-deployment (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mem9")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `site/public/beta/SKILL.md` | **Beta** SKILL.md — served at `https://mem9.ai/beta/SKILL.md` |' in text, "expected to find: " + '| `site/public/beta/SKILL.md` | **Beta** SKILL.md — served at `https://mem9.ai/beta/SKILL.md` |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `site/public/SKILL.md` — production, changes go live within seconds after merging to `main`' in text, "expected to find: " + '- `site/public/SKILL.md` — production, changes go live within seconds after merging to `main`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `site/public/SKILL.md` | **Production** SKILL.md — served at `https://mem9.ai/SKILL.md` |' in text, "expected to find: " + '| `site/public/SKILL.md` | **Production** SKILL.md — served at `https://mem9.ai/SKILL.md` |'[:80]

