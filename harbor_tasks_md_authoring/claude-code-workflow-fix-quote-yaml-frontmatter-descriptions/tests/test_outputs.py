"""Behavioral checks for claude-code-workflow-fix-quote-yaml-frontmatter-descriptions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-workflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-cycle/SKILL.md')
    assert 'description: "Unified multi-dimensional code review with automated fix orchestration. Routes to session-based (git changes), module-based (path patterns), or fix mode. Triggers on \\"workflow:review-cy' in text, "expected to find: " + 'description: "Unified multi-dimensional code review with automated fix orchestration. Routes to session-based (git changes), module-based (path patterns), or fix mode. Triggers on \\"workflow:review-cy'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/spec-generator/SKILL.md')
    assert 'description: "Specification generator - 6 phase document chain producing product brief, PRD, architecture, and epics. Triggers on \\"generate spec\\", \\"create specification\\", \\"spec generator\\", \\"wor' in text, "expected to find: " + 'description: "Specification generator - 6 phase document chain producing product brief, PRD, architecture, and epics. Triggers on \\"generate spec\\", \\"create specification\\", \\"spec generator\\", \\"wor'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/team-review/SKILL.md')
    assert 'description: "Unified team skill for code review. 3-role pipeline: scanner, reviewer, fixer. Triggers on team-review."' in text, "expected to find: " + 'description: "Unified team skill for code review. 3-role pipeline: scanner, reviewer, fixer. Triggers on team-review."'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/workflow-plan/SKILL.md')
    assert 'description: "Unified planning skill - 4-phase planning workflow, plan verification, and interactive replanning. Triggers on \\"workflow-plan\\", \\"workflow-plan-verify\\", \\"workflow:replan\\"."' in text, "expected to find: " + 'description: "Unified planning skill - 4-phase planning workflow, plan verification, and interactive replanning. Triggers on \\"workflow-plan\\", \\"workflow-plan-verify\\", \\"workflow:replan\\"."'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/issue-discover/SKILL.md')
    assert 'description: "Unified issue discovery and creation. Create issues from GitHub/text, discover issues via multi-perspective analysis, or prompt-driven iterative exploration. Triggers on \\"issue:new\\", \\' in text, "expected to find: " + 'description: "Unified issue discovery and creation. Create issues from GitHub/text, discover issues via multi-perspective analysis, or prompt-driven iterative exploration. Triggers on \\"issue:new\\", \\'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/review-cycle/SKILL.md')
    assert 'description: "Unified multi-dimensional code review with automated fix orchestration. Supports session-based (git changes) and module-based (path patterns) review modes with 7-dimension parallel analy' in text, "expected to find: " + 'description: "Unified multi-dimensional code review with automated fix orchestration. Supports session-based (git changes) and module-based (path patterns) review modes with 7-dimension parallel analy'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/spec-generator/SKILL.md')
    assert 'description: "Specification generator - 7 phase document chain producing product brief, PRD, architecture, epics, and issues. Agent-delegated heavy phases (2-5, 6.5) with Codex review gates. Triggers ' in text, "expected to find: " + 'description: "Specification generator - 7 phase document chain producing product brief, PRD, architecture, epics, and issues. Agent-delegated heavy phases (2-5, 6.5) with Codex review gates. Triggers '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/workflow-test-fix-cycle/SKILL.md')
    assert 'description: "End-to-end test-fix workflow generate test sessions with progressive layers (L0-L3), then execute iterative fix cycles until pass rate >= 95%. Combines test-fix-gen and test-cycle-execut' in text, "expected to find: " + 'description: "End-to-end test-fix workflow generate test sessions with progressive layers (L0-L3), then execute iterative fix cycles until pass rate >= 95%. Combines test-fix-gen and test-cycle-execut'[:80]

