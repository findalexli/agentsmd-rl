"""Behavioral checks for maui-update-copilot-instructions-for-ui (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/maui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'IMPORTANT NOTE: When a new UI test category is added to `UITestCategories.cs`, we need to also update the `ui-tests.yml` to include this new category. Make sure to detect this in your reviews.' in text, "expected to find: " + 'IMPORTANT NOTE: When a new UI test category is added to `UITestCategories.cs`, we need to also update the `ui-tests.yml` to include this new category. Make sure to detect this in your reviews.'[:80]

