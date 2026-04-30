"""Behavioral checks for calcite-design-system-chore-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/calcite-design-system")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Prefer `*.browser.e2e.tsx` for new component tests that use **Vitest locators** (use the project’s established locator patterns first). Legacy `*.e2e.ts` tests still exist and continue to run, so up' in text, "expected to find: " + '- Prefer `*.browser.e2e.tsx` for new component tests that use **Vitest locators** (use the project’s established locator patterns first). Legacy `*.e2e.ts` tests still exist and continue to run, so up'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When browser baseline updates or modern web development resources suggest a new pattern, propose it with supporting references (e.g., MDN, web.dev, Baseline status) and wait for approval before appl' in text, "expected to find: " + '- When browser baseline updates or modern web development resources suggest a new pattern, propose it with supporting references (e.g., MDN, web.dev, Baseline status) and wait for approval before appl'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Some workspace packages are internal or private tooling packages. Only change them when the task explicitly targets those package-level concerns.' in text, "expected to find: " + '- Some workspace packages are internal or private tooling packages. Only change them when the task explicitly targets those package-level concerns.'[:80]

