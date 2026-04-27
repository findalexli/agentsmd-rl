"""Behavioral checks for vitess-claudemd-add-missing-patterns-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Reuse existing helpers** - Before writing new parsing/validation code, check for existing utilities (e.g., `sqlerror` package for MySQL error codes, `mysqlctl.ParseVersionString()`, `strings.Split' in text, "expected to find: " + '- **Reuse existing helpers** - Before writing new parsing/validation code, check for existing utilities (e.g., `sqlerror` package for MySQL error codes, `mysqlctl.ParseVersionString()`, `strings.Split'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Use the `_test.go` suffix for mocks and test helpers that are only used by the current package's tests; if helpers or mocks need to be imported by other packages' tests or fuzz harnesses, put them i" in text, "expected to find: " + "- Use the `_test.go` suffix for mocks and test helpers that are only used by the current package's tests; if helpers or mocks need to be imported by other packages' tests or fuzz harnesses, put them i"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Structured logging** - New log messages should use structured logging with `slog`-style fields (e.g., `log.Warn("message", slog.Any("error", err))`) rather than printf-style logging with format st' in text, "expected to find: " + '- **Structured logging** - New log messages should use structured logging with `slog`-style fields (e.g., `log.Warn("message", slog.Any("error", err))`) rather than printf-style logging with format st'[:80]

