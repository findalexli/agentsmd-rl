"""Behavioral checks for everything-claude-code-featskills-add-blueprint-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert 'Produces a plan with parallel steps where possible (e.g., "implement Anthropic plugin" and "implement OpenAI plugin" run in parallel after the plugin interface step is done), model tier assignments (s' in text, "expected to find: " + 'Produces a plan with parallel steps where possible (e.g., "implement Anthropic plugin" and "implement OpenAI plugin" run in parallel after the plugin interface step is done), model tier assignments (s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert 'If you are vendoring only this skill outside the full ECC install, copy the reviewed file from the ECC repository into `~/.claude/skills/blueprint/SKILL.md`. Vendored copies do not have a git remote, ' in text, "expected to find: " + 'If you are vendoring only this skill outside the full ECC install, copy the reviewed file from the ECC repository into `~/.claude/skills/blueprint/SKILL.md`. Vendored copies do not have a git remote, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/blueprint/SKILL.md')
    assert '- **Zero runtime risk** — Pure Markdown skill. The entire repository contains only `.md` files — no hooks, no shell scripts, no executable code, no `package.json`, no build step. Nothing runs on insta' in text, "expected to find: " + '- **Zero runtime risk** — Pure Markdown skill. The entire repository contains only `.md` files — no hooks, no shell scripts, no executable code, no `package.json`, no build step. Nothing runs on insta'[:80]

