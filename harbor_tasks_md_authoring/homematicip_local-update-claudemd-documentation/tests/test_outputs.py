"""Behavioral checks for homematicip_local-update-claudemd-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/homematicip-local")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **aiohomematic** (v2025.12.17) - Core async library for Homematic device communication' in text, "expected to find: " + '- **aiohomematic** (v2025.12.17) - Core async library for Homematic device communication'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **pytest-homeassistant-custom-component** (0.13.300) - HA test framework' in text, "expected to find: " + '- **pytest-homeassistant-custom-component** (0.13.300) - HA test framework'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **aiohomematic-test-support** (2025.12.17) - Mock test data' in text, "expected to find: " + '- **aiohomematic-test-support** (2025.12.17) - Mock test data'[:80]

