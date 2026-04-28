"""Behavioral checks for sentry-ref-consolidate-ai-rules-into (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python.mdc')
    assert '.cursor/rules/python.mdc' in text, "expected to find: " + '.cursor/rules/python.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typescript_tests.mdc')
    assert '.cursor/rules/typescript_tests.mdc' in text, "expected to find: " + '.cursor/rules/typescript_tests.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**ALWAYS activate the virtualenv before any Python operation**: Before running any Python command (e.g. `python -c`), Python package (e.g. `pytest`, `mypy`), or Python script, you MUST first activate ' in text, "expected to find: " + '**ALWAYS activate the virtualenv before any Python operation**: Before running any Python command (e.g. `python -c`), Python package (e.g. `pytest`, `mypy`), or Python script, you MUST first activate '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **IMPORTANT**: AGENTS.md files are the source of truth for AI agent instructions. Always update the relevant AGENTS.md file when adding or modifying agent guidance. do not add to CLAUDE.md or cursor' in text, "expected to find: " + '> **IMPORTANT**: AGENTS.md files are the source of truth for AI agent instructions. Always update the relevant AGENTS.md file when adding or modifying agent guidance. do not add to CLAUDE.md or cursor'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Sentry is a developer-first error tracking and performance monitoring platform. This repository contains the main Sentry application, which is a large-scale Django application with a React frontend.' in text, "expected to find: " + 'Sentry is a developer-first error tracking and performance monitoring platform. This repository contains the main Sentry application, which is a large-scale Django application with a React frontend.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Sentry fixtures are located in tests/js/fixtures/ while GetSentry fixtures are located in tests/js/getsentry-test/fixtures/.' in text, "expected to find: " + 'Sentry fixtures are located in tests/js/fixtures/ while GetSentry fixtures are located in tests/js/getsentry-test/fixtures/.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert '- **Do not share state between tests**: Behavior should not be influenced by other tests in the test suite.' in text, "expected to find: " + '- **Do not share state between tests**: Behavior should not be influenced by other tests in the test suite.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert '**Always** import from `sentry-test/reactTestingLibrary`, not directly from `@testing-library/react`:' in text, "expected to find: " + '**Always** import from `sentry-test/reactTestingLibrary`, not directly from `@testing-library/react`:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('static/CLAUDE.md')
    assert 'static/CLAUDE.md' in text, "expected to find: " + 'static/CLAUDE.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('static/CLAUDE.md')
    assert 'static/CLAUDE.md' in text, "expected to find: " + 'static/CLAUDE.md'[:80]

