"""Behavioral checks for dd-trace-dotnet-convert-claude-commands-to-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dd-trace-dotnet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-crash/SKILL.md')
    assert 'description: Stack Trace Crash Analysis for dd-trace-dotnet' in text, "expected to find: " + 'description: Stack Trace Crash Analysis for dd-trace-dotnet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-crash/SKILL.md')
    assert 'argument-hint: <paste-stack-trace>' in text, "expected to find: " + 'argument-hint: <paste-stack-trace>'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-crash/SKILL.md')
    assert 'disable-model-invocation: true' in text, "expected to find: " + 'disable-model-invocation: true'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-error/SKILL.md')
    assert 'description: Error Stack Trace Analysis for dd-trace-dotnet' in text, "expected to find: " + 'description: Error Stack Trace Analysis for dd-trace-dotnet'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-error/SKILL.md')
    assert 'argument-hint: <paste-error-stack-trace>' in text, "expected to find: " + 'argument-hint: <paste-error-stack-trace>'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/analyze-error/SKILL.md')
    assert 'disable-model-invocation: true' in text, "expected to find: " + 'disable-model-invocation: true'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr comment:*), Bash(gh --version), Bash(gh auth status)' in text, "expected to find: " + 'allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr comment:*), Bash(gh --version), Bash(gh auth status)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'disable-model-invocation: true' in text, "expected to find: " + 'disable-model-invocation: true'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'agent: general-purpose' in text, "expected to find: " + 'agent: general-purpose'[:80]

