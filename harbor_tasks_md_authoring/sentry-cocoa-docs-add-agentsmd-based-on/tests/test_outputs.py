"""Behavioral checks for sentry-cocoa-docs-add-agentsmd-based-on (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry-cocoa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/file-filters.mdc')
    assert '.cursor/rules/file-filters.mdc' in text, "expected to find: " + '.cursor/rules/file-filters.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/github-workflow.mdc')
    assert '.cursor/rules/github-workflow.mdc' in text, "expected to find: " + '.cursor/rules/github-workflow.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Context Management**: When using compaction (which reduces context by summarizing older messages), the agent must re-read AGENTS.md afterwards to ensure it's always fully available in context. Thi" in text, "expected to find: " + "- **Context Management**: When using compaction (which reduces context by summarizing older messages), the agent must re-read AGENTS.md afterwards to ensure it's always fully available in context. Thi"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Pre-commit Hooks**: This repository uses pre-commit hooks. If a commit fails because files were changed during the commit process (e.g., by formatting hooks), automatically retry the commit. Pre-c' in text, "expected to find: " + '- **Pre-commit Hooks**: This repository uses pre-commit hooks. If a commit fails because files were changed during the commit process (e.g., by formatting hooks), automatically retry the commit. Pre-c'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Continuous Learning**: Whenever an agent performs a task and discovers new patterns, conventions, or best practices that aren't documented here, it should add these learnings to AGENTS.md. This en" in text, "expected to find: " + "- **Continuous Learning**: Whenever an agent performs a task and discovers new patterns, conventions, or best practices that aren't documented here, it should add these learnings to AGENTS.md. This en"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**ALWAYS adhere to AGENTS.md at all times.** This file contains comprehensive development patterns, conventions, and best practices for the Sentry Cocoa SDK project.' in text, "expected to find: " + '**ALWAYS adhere to AGENTS.md at all times.** This file contains comprehensive development patterns, conventions, and best practices for the Sentry Cocoa SDK project.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Follow Conventions**: All code, commits, and PRs must follow the patterns documented in AGENTS.md:' in text, "expected to find: " + '3. **Follow Conventions**: All code, commits, and PRs must follow the patterns documented in AGENTS.md:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **No AI References**: NEVER mention AI assistant names (Claude, ChatGPT, Cursor, etc.) in:' in text, "expected to find: " + '2. **No AI References**: NEVER mention AI assistant names (Claude, ChatGPT, Cursor, etc.) in:'[:80]

