"""Behavioral checks for vscode-coder-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-coder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "You're an experienced, pragmatic engineer. We're colleagues - push back on bad ideas and speak up when something doesn't make sense. Honesty over agreeableness." in text, "expected to find: " + "You're an experienced, pragmatic engineer. We're colleagues - push back on bad ideas and speak up when something doesn't make sense. Honesty over agreeableness."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Unit test files must be named `*.test.ts` and use Vitest, they should be placed in `./test/unit/<path in src>`' in text, "expected to find: " + '- Unit test files must be named `*.test.ts` and use Vitest, they should be placed in `./test/unit/<path in src>`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Run specific integration test: `yarn test:integration ./test/integration/filename.test.ts`' in text, "expected to find: " + '- Run specific integration test: `yarn test:integration ./test/integration/filename.test.ts`'[:80]

