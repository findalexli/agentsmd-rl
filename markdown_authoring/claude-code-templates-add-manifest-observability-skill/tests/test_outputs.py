"""Behavioral checks for claude-code-templates-add-manifest-observability-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/manifest/SKILL.md')
    assert 'description: Install and configure the Manifest observability plugin for your agents. Use when setting up telemetry, configuring API keys or endpoints, troubleshooting plugin connection issues, or ver' in text, "expected to find: " + 'description: Install and configure the Manifest observability plugin for your agents. Use when setting up telemetry, configuring API keys or endpoints, troubleshooting plugin connection issues, or ver'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/manifest/SKILL.md')
    assert 'Set up real-time observability for your AI agents with the Manifest plugin. Monitors costs, tokens, messages, and performance via OTLP telemetry.' in text, "expected to find: " + 'Set up real-time observability for your AI agents with the Manifest plugin. Monitors costs, tokens, messages, and performance via OTLP telemetry.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/manifest/SKILL.md')
    assert "Wait for a key starting with `mnfst_`. If the key doesn't match, tell the user the format looks incorrect and ask them to try again." in text, "expected to find: " + "Wait for a key starting with `mnfst_`. If the key doesn't match, tell the user the format looks incorrect and ask them to try again."[:80]

