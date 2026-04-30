"""Behavioral checks for jira-skill-fixskill-use-claudeskilldir-for-script (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jira-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-communication/SKILL.md')
    assert 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-search.py query "project = PROJ ORDER BY updated DESC" -n 5 -f key,summary,status,priority' in text, "expected to find: " + 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-search.py query "project = PROJ ORDER BY updated DESC" -n 5 -f key,summary,status,priority'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-communication/SKILL.md')
    assert 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --fields-json \'{"description": "New desc"}\'' in text, "expected to find: " + 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --fields-json \'{"description": "New desc"}\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-communication/SKILL.md')
    assert 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --priority Critical --summary "New title"' in text, "expected to find: " + 'uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --priority Critical --summary "New title"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-syntax/SKILL.md')
    assert '- `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh` - Automated syntax checker' in text, "expected to find: " + '- `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh` - Automated syntax checker'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-syntax/SKILL.md')
    assert '${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh path/to/content.txt' in text, "expected to find: " + '${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh path/to/content.txt'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-syntax/SKILL.md')
    assert '3. Validate with `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh`' in text, "expected to find: " + '3. Validate with `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh`'[:80]

