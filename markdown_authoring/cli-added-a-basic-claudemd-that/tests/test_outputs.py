"""Behavioral checks for cli-added-a-basic-claudemd-that (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'See @../.cursor/rules/docs.mdc for details on Shopify CLI architecture and conventions.' in text, "expected to find: " + 'See @../.cursor/rules/docs.mdc for details on Shopify CLI architecture and conventions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'See @../.cursor/rules/base.mdc for information on your desired behavior.' in text, "expected to find: " + 'See @../.cursor/rules/base.mdc for information on your desired behavior.'[:80]

