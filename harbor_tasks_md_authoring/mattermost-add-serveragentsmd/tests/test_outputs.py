"""Behavioral checks for mattermost-add-serveragentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mattermost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('server/AGENTS.md')
    assert 'Never run `go mod tidy` directly. Always run `make modules-tidy` instead — it excludes private enterprise imports that would otherwise break the tidy.' in text, "expected to find: " + 'Never run `go mod tidy` directly. Always run `make modules-tidy` instead — it excludes private enterprise imports that would otherwise break the tidy.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('server/AGENTS.md')
    assert 'After editing `i18n/en.json`, always run `make i18n-extract` — it regenerates the file with strings in the required order.' in text, "expected to find: " + 'After editing `i18n/en.json`, always run `make i18n-extract` — it regenerates the file with strings in the required order.'[:80]

