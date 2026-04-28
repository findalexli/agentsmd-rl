"""Behavioral checks for stackrox-choreai-add-pr-creation-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stackrox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- generally: conventional commit format (e.g., `fix(ui): description`) OR JIRA format (e.g., `ROX-123: description`)' in text, "expected to find: " + '- generally: conventional commit format (e.g., `fix(ui): description`) OR JIRA format (e.g., `ROX-123: description`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- include: problem definition, considered alternatives, explain whys for chosen solution, if applicable.' in text, "expected to find: " + '- include: problem definition, considered alternatives, explain whys for chosen solution, if applicable.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PR title must follow the format enforced by `.github/workflows/check-pr-title.yaml`' in text, "expected to find: " + '- PR title must follow the format enforced by `.github/workflows/check-pr-title.yaml`'[:80]

