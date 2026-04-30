"""Behavioral checks for autoresearch-feat-enforce-mandatory-askuserquestion-gate (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autoresearch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/SKILL.md')
    assert '**CRITICAL: If ANY critical field is missing (Goal, Scope, Metric, Direction, or Verify), you MUST use `AskUserQuestion` to collect them interactively. DO NOT proceed to The Loop or any execution phas' in text, "expected to find: " + '**CRITICAL: If ANY critical field is missing (Goal, Scope, Metric, Direction, or Verify), you MUST use `AskUserQuestion` to collect them interactively. DO NOT proceed to The Loop or any execution phas'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/SKILL.md')
    assert '**IMPORTANT:** You MUST call `AskUserQuestion` with batched questions — never ask one at a time, and never skip this step. Users should see all config choices together for full context. DO NOT proceed' in text, "expected to find: " + '**IMPORTANT:** You MUST call `AskUserQuestion` with batched questions — never ask one at a time, and never skip this step. Users should see all config choices together for full context. DO NOT proceed'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/SKILL.md')
    assert '2. **If ANY required context is missing → you MUST use `AskUserQuestion` to collect it BEFORE proceeding to any execution phase.** DO NOT skip this step. DO NOT proceed without user input.' in text, "expected to find: " + '2. **If ANY required context is missing → you MUST use `AskUserQuestion` to collect it BEFORE proceeding to any execution phase.** DO NOT skip this step. DO NOT proceed without user input.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/debug-workflow.md')
    assert '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:debug` is invoked without `--scope` or `--symptom`, you MUST use `AskUserQuestion` to gather full context BEFORE proceeding to ANY phase. DO NOT' in text, "expected to find: " + '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:debug` is invoked without `--scope` or `--symptom`, you MUST use `AskUserQuestion` to gather full context BEFORE proceeding to ANY phase. DO NOT'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/debug-workflow.md')
    assert '**STOP: Have you completed the Interactive Setup above?** If invoked without `--scope`/`--symptom` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.' in text, "expected to find: " + '**STOP: Have you completed the Interactive Setup above?** If invoked without `--scope`/`--symptom` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/debug-workflow.md')
    assert 'Scan the codebase first (run tests, lint, typecheck) to detect existing failures and provide smart defaults.' in text, "expected to find: " + 'Scan the codebase first (run tests, lint, typecheck) to detect existing failures and provide smart defaults.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/fix-workflow.md')
    assert '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:fix` is invoked without explicit `--target`, `--guard`, or `--scope`, you MUST first auto-detect all failures, then use `AskUserQuestion` to gat' in text, "expected to find: " + '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:fix` is invoked without explicit `--target`, `--guard`, or `--scope`, you MUST first auto-detect all failures, then use `AskUserQuestion` to gat'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/fix-workflow.md')
    assert '**STOP: Have you completed the Interactive Setup above?** If invoked without `--target`/`--guard`/`--scope` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.' in text, "expected to find: " + '**STOP: Have you completed the Interactive Setup above?** If invoked without `--target`/`--guard`/`--scope` flags, you MUST complete the `AskUserQuestion` call above BEFORE entering this phase.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/fix-workflow.md')
    assert 'You MUST call `AskUserQuestion` with all 4 questions in ONE call:' in text, "expected to find: " + 'You MUST call `AskUserQuestion` with all 4 questions in ONE call:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/plan-workflow.md')
    assert '**CRITICAL — BLOCKING PREREQUISITE:** If no goal is provided inline, you MUST use `AskUserQuestion` to capture it. DO NOT skip this step or proceed to Phase 2 without a goal.' in text, "expected to find: " + '**CRITICAL — BLOCKING PREREQUISITE:** If no goal is provided inline, you MUST use `AskUserQuestion` to capture it. DO NOT skip this step or proceed to Phase 2 without a goal.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/security-workflow.md')
    assert '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:security` is invoked without `--diff`, scope, or focus, you MUST scan the codebase first, then use `AskUserQuestion` to gather user input BEFORE' in text, "expected to find: " + '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:security` is invoked without `--diff`, scope, or focus, you MUST scan the codebase first, then use `AskUserQuestion` to gather user input BEFORE'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/security-workflow.md')
    assert 'You MUST call `AskUserQuestion` with all 3 questions in ONE call:' in text, "expected to find: " + 'You MUST call `AskUserQuestion` with all 3 questions in ONE call:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/security-workflow.md')
    assert '## PREREQUISITE: Interactive Setup (when invoked without flags)' in text, "expected to find: " + '## PREREQUISITE: Interactive Setup (when invoked without flags)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/ship-workflow.md')
    assert '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:ship` is invoked without `--type` or target, you MUST scan for staged changes, open PRs, and recent commits, then use `AskUserQuestion` to gathe' in text, "expected to find: " + '**CRITICAL — BLOCKING PREREQUISITE:** If `/autoresearch:ship` is invoked without `--type` or target, you MUST scan for staged changes, open PRs, and recent commits, then use `AskUserQuestion` to gathe'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/ship-workflow.md')
    assert 'You MUST call `AskUserQuestion` with all 3 questions in ONE call:' in text, "expected to find: " + 'You MUST call `AskUserQuestion` with all 3 questions in ONE call:'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/autoresearch/references/ship-workflow.md')
    assert '## PREREQUISITE: Interactive Setup (when invoked without flags)' in text, "expected to find: " + '## PREREQUISITE: Interactive Setup (when invoked without flags)'[:80]

