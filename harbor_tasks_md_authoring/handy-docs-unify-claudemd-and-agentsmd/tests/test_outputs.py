"""Behavioral checks for handy-docs-unify-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/handy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The app enforces single instance behavior — launching when already running brings the settings window to front rather than creating a new process. Remote control flags (`--toggle-transcription`, etc.)' in text, "expected to find: " + 'The app enforces single instance behavior — launching when already running brings the settings window to front rather than creating a new process. Remote control flags (`--toggle-transcription`, etc.)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and [PR template](.github/PULL_REQUEST_TEMPLATE.md) when submitting pull requests. For translations, see [CONTRIBUTING_TRANSLATIONS.md](' in text, "expected to find: " + 'Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and [PR template](.github/PULL_REQUEST_TEMPLATE.md) when submitting pull requests. For translations, see [CONTRIBUTING_TRANSLATIONS.md]('[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Note:** Feature freeze is active — bug fixes are top priority. New features require community support via [Discussions](https://github.com/cjpais/Handy/discussions).' in text, "expected to find: " + '**Note:** Feature freeze is active — bug fixes are top priority. New features require community support via [Discussions](https://github.com/cjpais/Handy/discussions).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read @AGENTS.md' in text, "expected to find: " + 'Read @AGENTS.md'[:80]

