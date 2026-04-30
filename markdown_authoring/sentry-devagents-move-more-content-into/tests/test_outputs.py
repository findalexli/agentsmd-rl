"""Behavioral checks for sentry-devagents-move-more-content-into (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '> **IMPORTANT**: AGENTS.md files are the source of truth for AI agent instructions. Always update the relevant AGENTS.md file when adding or modifying agent guidance. Do not add to CLAUDE.md or Cursor' in text, "expected to find: " + '> **IMPORTANT**: AGENTS.md files are the source of truth for AI agent instructions. Always update the relevant AGENTS.md file when adding or modifying agent guidance. Do not add to CLAUDE.md or Cursor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For frontend development patterns, commands, design system guidelines, and React testing best practices, see `static/AGENTS.md`.' in text, "expected to find: " + 'For frontend development patterns, commands, design system guidelines, and React testing best practices, see `static/AGENTS.md`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For backend development patterns, commands, security guidelines, and architecture, see `src/AGENTS.md`.' in text, "expected to find: " + 'For backend development patterns, commands, security guidelines, and architecture, see `src/AGENTS.md`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert 'When project IDs are passed in the request (query string or body), NEVER directly access or trust `request.data["project_id"]` or `request.GET["project_id"]`. Instead, use the endpoint\'s `self.get_pro' in text, "expected to find: " + 'When project IDs are passed in the request (query string or body), NEVER directly access or trust `request.data["project_id"]` or `request.GET["project_id"]`. Instead, use the endpoint\'s `self.get_pro'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert "**Indirect Object Reference** vulnerabilities occur when an attacker can access resources they shouldn't by manipulating IDs passed in requests. This is one of the most critical security issues in mul" in text, "expected to find: " + "**Indirect Object Reference** vulnerabilities occur when an attacker can access resources they shouldn't by manipulating IDs passed in requests. This is one of the most critical security issues in mul"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('src/AGENTS.md')
    assert "This ensures you're using the correct Python interpreter and dependencies from `.venv`. Commands will fail or use the wrong Python environment without this step." in text, "expected to find: " + "This ensures you're using the correct Python interpreter and dependencies from `.venv`. Commands will fail or use the wrong Python environment without this step."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert '**Always** import from `sentry-test/reactTestingLibrary`, not directly from `@testing-library/react`:' in text, "expected to find: " + '**Always** import from `sentry-test/reactTestingLibrary`, not directly from `@testing-library/react`:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert '3. NO CSS files (use [core components](./app/components/core/) or Emotion in edge cases)' in text, "expected to find: " + '3. NO CSS files (use [core components](./app/components/core/) or Emotion in edge cases)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'pnpm run lint:js components/avatar.tsx [...other files]' in text, "expected to find: " + 'pnpm run lint:js components/avatar.tsx [...other files]'[:80]

