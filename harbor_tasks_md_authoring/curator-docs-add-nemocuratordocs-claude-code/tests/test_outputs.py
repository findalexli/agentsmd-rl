"""Behavioral checks for curator-docs-add-nemocuratordocs-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/curator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/nemo-curator-docs/SKILL.md')
    assert 'Tokens like `{{ product_name }}`, `{{ container_version }}`, `{{ current_release }}`, `{{ github_repo }}`, `{{ min_python_version }}` are resolved by `fern/substitute_variables.py` at CI time. Use the' in text, "expected to find: " + 'Tokens like `{{ product_name }}`, `{{ container_version }}`, `{{ current_release }}`, `{{ github_repo }}`, `{{ min_python_version }}` are resolved by `fern/substitute_variables.py` at CI time. Use the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/nemo-curator-docs/SKILL.md')
    assert '**Merging to `main` does NOT publish.** Production only updates when a tag matching `docs/v*` is pushed (or the workflow is manually dispatched from the **Actions** tab). Do not push tags unless the u' in text, "expected to find: " + '**Merging to `main` does NOT publish.** Production only updates when a tag matching `docs/v*` is pushed (or the workflow is manually dispatched from the **Actions** tab). Do not push tags unless the u'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/nemo-curator-docs/SKILL.md')
    assert '**ALL docs edits happen under `fern/`.** The legacy `docs/` directory is deprecated — do not add or move content into it. Release notes, migration guides, and every new page belong under `fern/`.' in text, "expected to find: " + '**ALL docs edits happen under `fern/`.** The legacy `docs/` directory is deprecated — do not add or move content into it. Release notes, migration guides, and every new page belong under `fern/`.'[:80]

