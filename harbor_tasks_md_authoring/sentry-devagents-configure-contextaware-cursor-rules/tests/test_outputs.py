"""Behavioral checks for sentry-devagents-configure-contextaware-cursor-rules (markdown_authoring task).

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
    text = _read('.cursor/rules/README.md')
    assert "This directory contains `.mdc` (Markdown with Cursor directives) files that configure context-aware loading of AGENTS.md files in Cursor's AI assistant." in text, "expected to find: " + "This directory contains `.mdc` (Markdown with Cursor directives) files that configure context-aware loading of AGENTS.md files in Cursor's AI assistant."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert 'When you edit a file, Cursor automatically loads the relevant AGENTS.md based on glob patterns:' in text, "expected to find: " + 'When you edit a file, Cursor automatically loads the relevant AGENTS.md based on glob patterns:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert '- **`frontend.mdc`** - Loads frontend patterns for TypeScript/JavaScript/CSS files' in text, "expected to find: " + '- **`frontend.mdc`** - Loads frontend patterns for TypeScript/JavaScript/CSS files'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert "- '!src/**/tests/**'" in text, "expected to find: " + "- '!src/**/tests/**'"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert '@file:src/AGENTS.md' in text, "expected to find: " + '@file:src/AGENTS.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert "- 'src/**/*.py'" in text, "expected to find: " + "- 'src/**/*.py'"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert "- 'static/**/*.{ts,tsx,js,jsx}'" in text, "expected to find: " + "- 'static/**/*.{ts,tsx,js,jsx}'"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert "- 'static/**/*.{css,scss}'" in text, "expected to find: " + "- 'static/**/*.{css,scss}'"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert '@file:static/AGENTS.md' in text, "expected to find: " + '@file:static/AGENTS.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert 'alwaysApply: true' in text, "expected to find: " + 'alwaysApply: true'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/general.mdc')
    assert '@file:AGENTS.md' in text, "expected to find: " + '@file:AGENTS.md'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests.mdc')
    assert "- 'src/**/tests/**/*.py'" in text, "expected to find: " + "- 'src/**/tests/**/*.py'"[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests.mdc')
    assert '@file:tests/AGENTS.md' in text, "expected to find: " + '@file:tests/AGENTS.md'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests.mdc')
    assert "- 'tests/**/*.py'" in text, "expected to find: " + "- 'tests/**/*.py'"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Cursor is configured to automatically load relevant AGENTS.md files based on the file being edited (via `.cursor/rules/*.mdc`). This provides context-specific guidance without token bloat:' in text, "expected to find: " + 'Cursor is configured to automatically load relevant AGENTS.md files based on the file being edited (via `.cursor/rules/*.mdc`). This provides context-specific guidance without token bloat:'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Note**: These `.mdc` files only _reference_ AGENTS.md files—they don't duplicate content. All actual guidance should be added to the appropriate AGENTS.md file, not to Cursor rules." in text, "expected to find: " + "**Note**: These `.mdc` files only _reference_ AGENTS.md files—they don't duplicate content. All actual guidance should be added to the appropriate AGENTS.md file, not to Cursor rules."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Editing `static/**/*.{ts,tsx,js,jsx}` → Loads `static/AGENTS.md` (frontend patterns)' in text, "expected to find: " + '- Editing `static/**/*.{ts,tsx,js,jsx}` → Loads `static/AGENTS.md` (frontend patterns)'[:80]

