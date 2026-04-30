"""Behavioral checks for mcp-context-forge-refactor-rewrite-prreview-skill-as (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-context-forge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '- `git diff origin/main..HEAD | bob "Review this diff for correctness, security, and design quality. Be specific about line-level issues."`' in text, "expected to find: " + '- `git diff origin/main..HEAD | bob "Review this diff for correctness, security, and design quality. Be specific about line-level issues."`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '| 9 | Alembic migrations | Conditional | Idempotence, reversibility, cross-DB compat, `batch_alter_table` for SQLite |' in text, "expected to find: " + '| 9 | Alembic migrations | Conditional | Idempotence, reversibility, cross-DB compat, `batch_alter_table` for SQLite |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert '| 4 | Linter compliance | Blocking | Run project linters on touched files; report findings with exact commands |' in text, "expected to find: " + '| 4 | Linter compliance | Blocking | Run project linters on touched files; report findings with exact commands |'[:80]

