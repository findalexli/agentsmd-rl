"""Behavioral checks for directus-docs-add-changeset-conventions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/directus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When creating a new pull request, always use the PR template located at `.github/pull_request_template.md`. The template' in text, "expected to find: " + 'When creating a new pull request, always use the PR template located at `.github/pull_request_template.md`. The template'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Replace the placeholder "Lorem ipsum" content with actual details about your changes. Always reference the related issue' in text, "expected to find: " + 'Replace the placeholder "Lorem ipsum" content with actual details about your changes. Always reference the related issue'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**IMPORTANT**: All changeset descriptions must be written in **past tense**, as they document changes that have already' in text, "expected to find: " + '**IMPORTANT**: All changeset descriptions must be written in **past tense**, as they document changes that have already'[:80]

