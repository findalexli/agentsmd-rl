"""Behavioral checks for framework-chore-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/framework")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- All sentinel errors must be declared in `errors/list.go` using the framework error constructor: `github.com/goravel/framework/errors.New(...)` (or unqualified `New(...)` when inside `package errors`' in text, "expected to find: " + '- All sentinel errors must be declared in `errors/list.go` using the framework error constructor: `github.com/goravel/framework/errors.New(...)` (or unqualified `New(...)` when inside `package errors`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use format verbs in error messages and supply dynamic parts via `.Args(...)` — never interpolate directly into the `New` string.' in text, "expected to find: " + '- Use format verbs in error messages and supply dynamic parts via `.Args(...)` — never interpolate directly into the `New` string.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do not shadow the built-in `error` type, the standard-library `errors` package, or common variable names (`err`, `ctx`, etc.).' in text, "expected to find: " + '- Do not shadow the built-in `error` type, the standard-library `errors` package, or common variable names (`err`, `ctx`, etc.).'[:80]

