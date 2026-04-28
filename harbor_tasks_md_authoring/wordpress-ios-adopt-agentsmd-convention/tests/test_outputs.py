"""Behavioral checks for wordpress-ios-adopt-agentsmd-convention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wordpress-ios")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Always check RELEASE-NOTES.txt file** (note: hyphen, not underscore) for developer-authored release notes under the version number section. These notes start with `[*]`, `[**]`, or `[***]` (stars ' in text, "expected to find: " + '- **Always check RELEASE-NOTES.txt file** (note: hyphen, not underscore) for developer-authored release notes under the version number section. These notes start with `[*]`, `[**]`, or `[***]` (stars '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Version 25.9**: Raw added in commits `ce08612ecc324e981ef9c5898c98bb267cf29721` & `30cd7073802feb8711b2aae8bb69f41fedba1d80`, editorialized in `bc3af0d2c0c8c3dec8556bb4eff7709f3c151c0d`' in text, "expected to find: " + '- **Version 25.9**: Raw added in commits `ce08612ecc324e981ef9c5898c98bb267cf29721` & `30cd7073802feb8711b2aae8bb69f41fedba1d80`, editorialized in `bc3af0d2c0c8c3dec8556bb4eff7709f3c151c0d`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Version 26.0**: Raw added in commits `8a9e79587924f85e6ac6756fe47d045f7db04ece` & `883acc3324abe45d0e121f3854dc84712b22b4cb`, editorialized in `2ef13c2898c5b58d09c8a3af9f109a47f0bd782c`' in text, "expected to find: " + '- **Version 26.0**: Raw added in commits `8a9e79587924f85e6ac6756fe47d045f7db04ece` & `883acc3324abe45d0e121f3854dc84712b22b4cb`, editorialized in `2ef13c2898c5b58d09c8a3af9f109a47f0bd782c`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

