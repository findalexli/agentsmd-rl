"""Behavioral checks for habitat-creates-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/habitat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Remember**: Always follow the prompt-based workflow, asking for confirmation before proceeding to each next step, and maintain the >80% test coverage requirement throughout development.' in text, "expected to find: " + '**Remember**: Always follow the prompt-based workflow, asking for confirmation before proceeding to each next step, and maintain the >80% test coverage requirement throughout development.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Habitat is Chef's application automation framework that builds, deploys, and manages applications. This repository contains the core Habitat components written primarily in Rust." in text, "expected to find: " + "Habitat is Chef's application automation framework that builds, deploys, and manages applications. This repository contains the core Habitat components written primarily in Rust."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'gh pr create --title "<JIRA-ID>: Brief title" --body "<HTML formatted description>" --label "runtest:all:stable"' in text, "expected to find: " + 'gh pr create --title "<JIRA-ID>: Brief title" --body "<HTML formatted description>" --label "runtest:all:stable"'[:80]

