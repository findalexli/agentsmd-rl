"""Behavioral checks for antigravity-awesome-skills-feat-add-manifest-observability-s (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/manifest/SKILL.md')
    assert 'description: Install and configure the Manifest observability plugin for your agents. Use when setting up telemetry, configuring API keys, or troubleshooting the plugin.' in text, "expected to find: " + 'description: Install and configure the Manifest observability plugin for your agents. Use when setting up telemetry, configuring API keys, or troubleshooting the plugin.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/manifest/SKILL.md')
    assert 'Ask the user if they have a custom endpoint. If not, the default (`https://app.manifest.build/api/v1/otlp`) is used automatically. If they do:' in text, "expected to find: " + 'Ask the user if they have a custom endpoint. If not, the default (`https://app.manifest.build/api/v1/otlp`) is used automatically. If they do:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/manifest/SKILL.md')
    assert "Wait for a key starting with `mnfst_`. If the key doesn't match, tell the user the format looks incorrect and ask them to try again." in text, "expected to find: " + "Wait for a key starting with `mnfst_`. If the key doesn't match, tell the user the format looks incorrect and ask them to try again."[:80]

