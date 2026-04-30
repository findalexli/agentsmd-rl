"""Behavioral checks for mlflow-improve-claudemd-creating-pull-requests (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mlflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Follow [the PR template](./.github/pull_request_template.md) when creating pull requests. Remove any unused checkboxes from the template to keep your PR clean and focused.' in text, "expected to find: " + 'Follow [the PR template](./.github/pull_request_template.md) when creating pull requests. Remove any unused checkboxes from the template to keep your PR clean and focused.'[:80]

