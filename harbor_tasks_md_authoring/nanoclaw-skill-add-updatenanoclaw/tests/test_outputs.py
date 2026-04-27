"""Behavioral checks for nanoclaw-skill-add-updatenanoclaw (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert '**Preflight**: checks for clean working tree (`git status --porcelain`). If `upstream` remote is missing, asks you for the URL (defaults to `https://github.com/qwibitai/nanoclaw.git`) and adds it. Det' in text, "expected to find: " + '**Preflight**: checks for clean working tree (`git status --porcelain`). If `upstream` remote is missing, asks you for the URL (defaults to `https://github.com/qwibitai/nanoclaw.git`) and adds it. Det'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert '**Backup**: creates a timestamped backup branch and tag (`backup/pre-update-<hash>-<timestamp>`, `pre-update-<hash>-<timestamp>`) before touching anything. Safe to run multiple times.' in text, "expected to find: " + '**Backup**: creates a timestamped backup branch and tag (`backup/pre-update-<hash>-<timestamp>`, `pre-update-<hash>-<timestamp>`) before touching anything. Safe to run multiple times.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/update-nanoclaw/SKILL.md')
    assert '- Store this as UPSTREAM_BRANCH for all subsequent commands. Every command below that references `upstream/main` should use `upstream/$UPSTREAM_BRANCH` instead.' in text, "expected to find: " + '- Store this as UPSTREAM_BRANCH for all subsequent commands. Every command below that references `upstream/main` should use `upstream/$UPSTREAM_BRANCH` instead.'[:80]

