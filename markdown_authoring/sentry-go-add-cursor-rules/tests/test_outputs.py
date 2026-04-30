"""Behavioral checks for sentry-go-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-go")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/changelog.mdc')
    assert '- Allow flush to be used multiple times without issues, particularly for the batch logger ([#1051](https://github.com/getsentry/sentry-go/pull/1051))' in text, "expected to find: " + '- Allow flush to be used multiple times without issues, particularly for the batch logger ([#1051](https://github.com/getsentry/sentry-go/pull/1051))'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/changelog.mdc')
    assert '- Fix race condition in `Scope.GetSpan()` method by adding proper mutex locking ([#1044](https://github.com/getsentry/sentry-go/pull/1044))' in text, "expected to find: " + '- Fix race condition in `Scope.GetSpan()` method by adding proper mutex locking ([#1044](https://github.com/getsentry/sentry-go/pull/1044))'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/changelog.mdc')
    assert '- Guard transport on `Close()` to prevent panic when called multiple times ([#1044](https://github.com/getsentry/sentry-go/pull/1044))' in text, "expected to find: " + '- Guard transport on `Close()` to prevent panic when called multiple times ([#1044](https://github.com/getsentry/sentry-go/pull/1044))'[:80]

