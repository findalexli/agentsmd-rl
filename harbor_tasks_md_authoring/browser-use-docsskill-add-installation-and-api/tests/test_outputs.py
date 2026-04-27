"""Behavioral checks for browser-use-docsskill-add-installation-and-api (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/browser-use")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert 'Some features (`run`, `extract`, `--browser remote`) require an API key. The CLI checks these locations in order:' in text, "expected to find: " + 'Some features (`run`, `extract`, `--browser remote`) require an API key. The CLI checks these locations in order:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert '7. **CLI aliases**: `bu`, `browser`, and `browseruse` all work identically to `browser-use`' in text, "expected to find: " + '7. **CLI aliases**: `bu`, `browser`, and `browseruse` all work identically to `browser-use`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/browser-use/SKILL.md')
    assert 'browser-use install                       # Install Chromium and system dependencies' in text, "expected to find: " + 'browser-use install                       # Install Chromium and system dependencies'[:80]

