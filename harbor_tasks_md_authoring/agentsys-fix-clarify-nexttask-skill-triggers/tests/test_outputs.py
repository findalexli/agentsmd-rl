"""Behavioral checks for agentsys-fix-clarify-nexttask-skill-triggers (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentsys")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('adapters/opencode/skills/discover-tasks/SKILL.md')
    assert 'description: "Use when user asks to \\"discover tasks\\", \\"find next task\\", or \\"prioritize issues\\". Discovers and ranks tasks from GitHub, GitLab, local files, and custom sources."' in text, "expected to find: " + 'description: "Use when user asks to \\"discover tasks\\", \\"find next task\\", or \\"prioritize issues\\". Discovers and ranks tasks from GitHub, GitLab, local files, and custom sources."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('adapters/opencode/skills/orchestrate-review/SKILL.md')
    assert 'description: "Use when user asks to \\"deep review the code\\", \\"thorough code review\\", \\"multi-pass review\\", or when orchestrating the Phase 9 review loop. Provides review pass definitions (code qua' in text, "expected to find: " + 'description: "Use when user asks to \\"deep review the code\\", \\"thorough code review\\", \\"multi-pass review\\", or when orchestrating the Phase 9 review loop. Provides review pass definitions (code qua'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('adapters/opencode/skills/validate-delivery/SKILL.md')
    assert 'description: "Use when user asks to \\"validate delivery\\", \\"check readiness\\", or \\"verify completion\\". Runs tests, build, and requirement checks with pass/fail instructions."' in text, "expected to find: " + 'description: "Use when user asks to \\"validate delivery\\", \\"check readiness\\", or \\"verify completion\\". Runs tests, build, and requirement checks with pass/fail instructions."'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/next-task/skills/discover-tasks/SKILL.md')
    assert 'description: "Use when user asks to \\"discover tasks\\", \\"find next task\\", or \\"prioritize issues\\". Discovers and ranks tasks from GitHub, GitLab, local files, and custom sources."' in text, "expected to find: " + 'description: "Use when user asks to \\"discover tasks\\", \\"find next task\\", or \\"prioritize issues\\". Discovers and ranks tasks from GitHub, GitLab, local files, and custom sources."'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/next-task/skills/orchestrate-review/SKILL.md')
    assert 'description: "Use when user asks to \\"deep review the code\\", \\"thorough code review\\", \\"multi-pass review\\", or when orchestrating the Phase 9 review loop. Provides review pass definitions (code qua' in text, "expected to find: " + 'description: "Use when user asks to \\"deep review the code\\", \\"thorough code review\\", \\"multi-pass review\\", or when orchestrating the Phase 9 review loop. Provides review pass definitions (code qua'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/next-task/skills/validate-delivery/SKILL.md')
    assert 'description: "Use when user asks to \\"validate delivery\\", \\"check readiness\\", or \\"verify completion\\". Runs tests, build, and requirement checks with pass/fail instructions."' in text, "expected to find: " + 'description: "Use when user asks to \\"validate delivery\\", \\"check readiness\\", or \\"verify completion\\". Runs tests, build, and requirement checks with pass/fail instructions."'[:80]

