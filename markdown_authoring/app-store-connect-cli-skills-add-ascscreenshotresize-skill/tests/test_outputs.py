"""Behavioral checks for app-store-connect-cli-skills-add-ascscreenshotresize-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/app-store-connect-cli-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-screenshot-resize/SKILL.md')
    assert 'Use this skill to resize screenshots to the exact pixel dimensions required by App Store Connect and validate they pass upload requirements. Uses the built-in macOS `sips` tool — no third-party depend' in text, "expected to find: " + 'Use this skill to resize screenshots to the exact pixel dimensions required by App Store Connect and validate they pass upload requirements. Uses the built-in macOS `sips` tool — no third-party depend'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-screenshot-resize/SKILL.md')
    assert 'macOS screenshots often contain hidden Unicode characters (e.g., `U+202F` narrow no-break space) that cause `sips` and other tools to fail with "not a valid file". Always sanitize first:' in text, "expected to find: " + 'macOS screenshots often contain hidden Unicode characters (e.g., `U+202F` narrow no-break space) that cause `sips` and other tools to fail with "not a valid file". Always sanitize first:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/asc-screenshot-resize/SKILL.md')
    assert 'description: Resize and validate App Store screenshots for all device classes using macOS sips. Use when preparing or fixing screenshots for App Store Connect submission.' in text, "expected to find: " + 'description: Resize and validate App Store screenshots for all device classes using macOS sips. Use when preparing or fixing screenshots for App Store Connect submission.'[:80]

