"""Behavioral checks for arturo-add-agentsmd-from-codex (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/arturo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs: follow `.github/pull_request_template.md`. Provide a clear description, scope (type checkboxes), linked issues, and screenshots/logs when relevant.' in text, "expected to find: " + '- PRs: follow `.github/pull_request_template.md`. Provide a clear description, scope (type checkboxes), linked issues, and screenshots/logs when relevant.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commits: imperative mood, concise subject; reference issues (e.g., `Fixes #123`). Group related changes; include tests/docs when applicable.' in text, "expected to find: " + '- Commits: imperative mood, concise subject; reference issues (e.g., `Fixes #123`). Group related changes; include tests/docs when applicable.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Test pattern: pair an `.art` script with a matching `.res` expected output in `tests/unittests/` (e.g., `strings.art` + `strings.res`).' in text, "expected to find: " + '- Test pattern: pair an `.art` script with a matching `.res` expected output in `tests/unittests/` (e.g., `strings.art` + `strings.res`).'[:80]

