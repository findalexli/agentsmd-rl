"""Behavioral checks for moai-adk-fixrouting-team-teammd-626 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/moai-adk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert 'If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. T' in text, "expected to find: " + 'If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. T'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert 'For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md (team mode: ${CLAUDE_SKILL_DIR}/team/plan.md)' in text, "expected to find: " + 'For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/plan.md (team mode: ${CLAUDE_SKILL_DIR}/team/plan.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/moai/SKILL.md')
    assert 'For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md (team mode: ${CLAUDE_SKILL_DIR}/team/sync.md)' in text, "expected to find: " + 'For detailed orchestration: Read ${CLAUDE_SKILL_DIR}/workflows/sync.md (team mode: ${CLAUDE_SKILL_DIR}/team/sync.md)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert 'If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. T' in text, "expected to find: " + 'If `--team` flag was parsed AND `${CLAUDE_SKILL_DIR}/team/<name>.md` exists for the target subcommand, read the team workflow file instead of the solo workflow. Otherwise read `workflows/<name>.md`. T'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert '| "The user\'s intent is obvious, no need for a Socratic interview" | Ambiguous verbs (clean, fix, improve) almost always produce wrong scope. Rule 5 exists because obvious is often wrong. |' in text, "expected to find: " + '| "The user\'s intent is obvious, no need for a Socratic interview" | Ambiguous verbs (clean, fix, improve) almost always produce wrong scope. Rule 5 exists because obvious is often wrong. |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('internal/template/templates/.claude/skills/moai/SKILL.md')
    assert '| "I can run /moai run without a SPEC, it is just a tweak" | Without a SPEC, there is no acceptance criterion to check. Every run without a SPEC silently degrades quality tracking. |' in text, "expected to find: " + '| "I can run /moai run without a SPEC, it is just a tweak" | Without a SPEC, there is no acceptance criterion to check. Every run without a SPEC silently degrades quality tracking. |'[:80]

