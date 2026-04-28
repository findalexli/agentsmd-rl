"""Behavioral checks for riverui-add-an-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/riverui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Tests: `npm run test`, `npm run test:once`, `npm exec -- vitest --run path/to/file.test.tsx`' in text, "expected to find: " + '- Tests: `npm run test`, `npm run test:once`, `npm exec -- vitest --run path/to/file.test.tsx`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- UI/router/search-state: targeted tests + `npm run lint`.' in text, "expected to find: " + '- UI/router/search-state: targeted tests + `npm run lint`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use auto-close keywords; don’t mention "ran lint/tests".' in text, "expected to find: " + '- Use auto-close keywords; don’t mention "ran lint/tests".'[:80]

