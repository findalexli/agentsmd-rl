"""Behavioral checks for compound-engineering-plugin-fixceupdate-replace-cache-sweep- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert '!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")")")" ;; *) echo \'__CE_UPDATE_NO' in text, "expected to find: " + '!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")")")" ;; *) echo \'__CE_UPDATE_NO'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert '!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")" ;; *) echo \'__CE_UPDATE_NOT_MARKETPLACE__\' ;; esac`' in text, "expected to find: " + '!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")" ;; *) echo \'__CE_UPDATE_NOT_MARKETPLACE__\' ;; esac`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert '`~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>/skills/ce-update`,' in text, "expected to find: " + '`~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>/skills/ce-update`,'[:80]

