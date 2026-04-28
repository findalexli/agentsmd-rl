"""Behavioral checks for zealot-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zealot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Frozen String Literals**: Always include `# frozen_string_literal: true` at the top of Ruby files (except config.ru, Gemfile, Rakefile, and config files)' in text, "expected to find: " + '- **Frozen String Literals**: Always include `# frozen_string_literal: true` at the top of Ruby files (except config.ru, Gemfile, Rakefile, and config files)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Zealot is an open-source self-hosted continuous integration platform for mobile app distribution. It provides:' in text, "expected to find: " + 'Zealot is an open-source self-hosted continuous integration platform for mobile app distribution. It provides:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This file provides guidance to GitHub Copilot when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to GitHub Copilot when working with code in this repository.'[:80]

