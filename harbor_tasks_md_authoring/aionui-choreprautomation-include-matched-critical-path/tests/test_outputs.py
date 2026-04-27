"""Behavioral checks for aionui-choreprautomation-include-matched-critical-path (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aionui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'Parse the `<!-- automation-result -->` block from the cached comment. Set `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` from it, then **skip to Step 7** (do not run pr-review again).' in text, "expected to find: " + 'Parse the `<!-- automation-result -->` block from the cached comment. Set `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` from it, then **skip to Step 7** (do not run pr-review again).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'CRITICAL_FILES=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")' in text, "expected to find: " + 'CRITICAL_FILES=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-automation/SKILL.md')
    assert 'Save `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` (override Step 5 values if different).' in text, "expected to find: " + 'Save `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` (override Step 5 values if different).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'CRITICAL_FILES=$(git diff origin/<baseRefName>...HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")' in text, "expected to find: " + 'CRITICAL_FILES=$(git diff origin/<baseRefName>...HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'When `IS_CRITICAL_PATH` is true, list matched files one per line:' in text, "expected to find: " + 'When `IS_CRITICAL_PATH` is true, list matched files one per line:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-review/SKILL.md')
    assert 'When a pattern is defined, check and capture matched files:' in text, "expected to find: " + 'When a pattern is defined, check and capture matched files:'[:80]

