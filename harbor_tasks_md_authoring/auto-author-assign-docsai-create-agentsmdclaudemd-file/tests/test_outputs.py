"""Behavioral checks for auto-author-assign-docsai-create-agentsmdclaudemd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-author-assign")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**auto-author-assign** is a GitHub Action that automatically assigns pull request (and optionally issue) authors as assignees. When a PR or issue is opened/reopened, this action assigns the author to ' in text, "expected to find: " + '**auto-author-assign** is a GitHub Action that automatically assigns pull request (and optionally issue) authors as assignees. When a PR or issue is opened/reopened, this action assigns the author to '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Always rebuild before committing**: After modifying `src/index.js`, run `npm run build` and commit the updated `dist/index.js`. The CI will fail if dist is out of sync.' in text, "expected to find: " + '- **Always rebuild before committing**: After modifying `src/index.js`, run `npm run build` and commit the updated `dist/index.js`. The CI will fail if dist is out of sync.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **No tests**: This project currently has no automated tests (`npm test` exits with error)' in text, "expected to find: " + '- **No tests**: This project currently has no automated tests (`npm test` exits with error)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

