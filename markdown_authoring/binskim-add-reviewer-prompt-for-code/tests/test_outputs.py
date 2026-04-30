"""Behavioral checks for binskim-add-reviewer-prompt-for-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/binskim")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/Reviewer.prompt.md')
    assert 'You are an expert code reviewer across multiple languages, frameworks, and production systems. Your role is to analyze code for correctness, security, performance, maintainability, and clarity. You id' in text, "expected to find: " + 'You are an expert code reviewer across multiple languages, frameworks, and production systems. Your role is to analyze code for correctness, security, performance, maintainability, and clarity. You id'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/Reviewer.prompt.md')
    assert '**Flag problematic patterns**: If the code follows an existing pattern that itself has quality issues (missing error handling, security gaps, etc.), flag both the code AND the problematic pattern. Not' in text, "expected to find: " + '**Flag problematic patterns**: If the code follows an existing pattern that itself has quality issues (missing error handling, security gaps, etc.), flag both the code AND the problematic pattern. Not'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/prompts/Reviewer.prompt.md')
    assert "**Escalate ambiguity, not clear fixes.** Security issues with obvious remediation—report normally. But if you can't assess severity, the fix is unclear, or it's an architectural concern—flag it to CoD" in text, "expected to find: " + "**Escalate ambiguity, not clear fixes.** Security issues with obvious remediation—report normally. But if you can't assess severity, the fix is unclear, or it's an architectural concern—flag it to CoD"[:80]

