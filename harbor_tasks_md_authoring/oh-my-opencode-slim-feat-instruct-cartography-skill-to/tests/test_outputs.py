"""Behavioral checks for oh-my-opencode-slim-feat-instruct-cartography-skill-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/oh-my-opencode-slim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/skills/cartography/SKILL.md')
    assert '**OpenCode auto-loads `AGENTS.md` into agent context on every session.** To ensure agents automatically discover and use the codemap, update (or create) `AGENTS.md` at the repo root:' in text, "expected to find: " + '**OpenCode auto-loads `AGENTS.md` into agent context on every session.** To ensure agents automatically discover and use the codemap, update (or create) `AGENTS.md` at the repo root:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/skills/cartography/SKILL.md')
    assert '1. If `AGENTS.md` already exists and already contains a `## Repository Map` section, **skip this step** — the reference is already set up.' in text, "expected to find: " + '1. If `AGENTS.md` already exists and already contains a `## Repository Map` section, **skip this step** — the reference is already set up.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/skills/cartography/SKILL.md')
    assert 'This is idempotent — repeated cartography runs will detect the existing section and skip. No duplication.' in text, "expected to find: " + 'This is idempotent — repeated cartography runs will detect the existing section and skip. No duplication.'[:80]

