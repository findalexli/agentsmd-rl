"""Behavioral checks for miuix-misc-embrace-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/miuix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For doc-related changes use `docs`; for build-related changes use `build`; for code fixes use `fix`; for general dependency updates use `fix(deps)`; for Gradle/build-tool dependency or configuration' in text, "expected to find: " + '- For doc-related changes use `docs`; for build-related changes use `build`; for code fixes use `fix`; for general dependency updates use `fix(deps)`; for Gradle/build-tool dependency or configuration'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Mirror existing history style: `<scope>: <summary>` with a short lowercase scope tied to the touched area (e.g., `library`, `docs`, `example`). Keep the summary concise, sentence case, and avoid tra' in text, "expected to find: " + '- Mirror existing history style: `<scope>: <summary>` with a short lowercase scope tied to the touched area (e.g., `library`, `docs`, `example`). Keep the summary concise, sentence case, and avoid tra'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Before committing, glance at recent `git log --oneline` to stay consistent with current prefixes and capitalization used in this repo.' in text, "expected to find: " + '- Before committing, glance at recent `git log --oneline` to stay consistent with current prefixes and capitalization used in this repo.'[:80]

