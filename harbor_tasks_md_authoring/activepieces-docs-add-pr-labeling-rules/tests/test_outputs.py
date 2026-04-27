"""Behavioral checks for activepieces-docs-add-pr-labeling-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/activepieces")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If the PR includes any contributions to pieces (integrations under `packages/pieces`), also add the **`pieces`** label (in addition to the primary label above).' in text, "expected to find: " + '- If the PR includes any contributions to pieces (integrations under `packages/pieces`), also add the **`pieces`** label (in addition to the primary label above).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When creating a PR with `gh pr create`, always apply exactly one of these labels based on the nature of the change:' in text, "expected to find: " + '- When creating a PR with `gh pr create`, always apply exactly one of these labels based on the nature of the change:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`skip-changelog`** — changes that should not appear in the changelog (docs, CI tweaks, internal refactors, etc.)' in text, "expected to find: " + '- **`skip-changelog`** — changes that should not appear in the changelog (docs, CI tweaks, internal refactors, etc.)'[:80]

