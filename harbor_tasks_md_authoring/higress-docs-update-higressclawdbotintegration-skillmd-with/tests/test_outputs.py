"""Behavioral checks for higress-docs-update-higressclawdbotintegration-skillmd-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/higress")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-clawdbot-integration/SKILL.md')
    assert '**Important:** API key changes take effect immediately via hot-reload. No container restart is required.' in text, "expected to find: " + '**Important:** API key changes take effect immediately via hot-reload. No container restart is required.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-clawdbot-integration/SKILL.md')
    assert '**Note:** Changes take effect immediately via hot-reload. No container restart required.' in text, "expected to find: " + '**Note:** Changes take effect immediately via hot-reload. No container restart required.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/higress-clawdbot-integration/SKILL.md')
    assert 'After deployment, use the `config` subcommand to manage LLM provider API keys:' in text, "expected to find: " + 'After deployment, use the `config` subcommand to manage LLM provider API keys:'[:80]

