"""Behavioral checks for obsidian-claude-pkm-add-checklinks-skill-for-broken (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/obsidian-claude-pkm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/check-links/SKILL.md')
    assert 'Finds broken `[[wiki-links]]` across your vault by extracting link targets and verifying that each target file exists. Read-only — never modifies files.' in text, "expected to find: " + 'Finds broken `[[wiki-links]]` across your vault by extracting link targets and verifying that each target file exists. Read-only — never modifies files.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/check-links/SKILL.md')
    assert 'description: Find broken wiki-links in the vault. Read-only analysis — scans for [[links]] and verifies target files exist. No writes, no dependencies.' in text, "expected to find: " + 'description: Find broken wiki-links in the vault. Read-only analysis — scans for [[links]] and verifies target files exist. No writes, no dependencies.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('vault-template/.claude/skills/check-links/SKILL.md')
    assert 'From the grep results, extract the unique link targets. For each match like `[[My Note]]` or `[[My Note|display text]]`, the target is `My Note`.' in text, "expected to find: " + 'From the grep results, extract the unique link targets. For each match like `[[My Note]]` or `[[My Note|display text]]`, the target is `My Note`.'[:80]

