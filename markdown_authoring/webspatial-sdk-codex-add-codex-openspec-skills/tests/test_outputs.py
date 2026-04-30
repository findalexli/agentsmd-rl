"""Behavioral checks for webspatial-sdk-codex-add-codex-openspec-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/webspatial-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-apply-change/SKILL.md')
    assert '**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.' in text, "expected to find: " + '**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-apply-change/SKILL.md')
    assert 'description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks.' in text, "expected to find: " + 'description: Implement tasks from an OpenSpec change. Use when the user wants to start implementing, continue implementation, or work through tasks.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-apply-change/SKILL.md')
    assert '- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions' in text, "expected to find: " + '- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-archive-change/SKILL.md')
    assert 'If user chooses sync, use Task tool (subagent_type: "general-purpose", prompt: "Use Skill tool to invoke openspec-sync-specs for change \'<name>\'. Delta spec analysis: <include the analyzed delta spec ' in text, "expected to find: " + 'If user chooses sync, use Task tool (subagent_type: "general-purpose", prompt: "Use Skill tool to invoke openspec-sync-specs for change \'<name>\'. Delta spec analysis: <include the analyzed delta spec '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-archive-change/SKILL.md')
    assert '**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.' in text, "expected to find: " + '**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-archive-change/SKILL.md')
    assert 'description: Archive a completed change in the experimental workflow. Use when the user wants to finalize and archive a change after implementation is complete.' in text, "expected to find: " + 'description: Archive a completed change in the experimental workflow. Use when the user wants to finalize and archive a change after implementation is complete.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-explore/SKILL.md')
    assert '**IMPORTANT: Explore mode is for thinking, not implementing.** You may read files, search code, and investigate the codebase, but you must NEVER write code or implement features. If the user asks you ' in text, "expected to find: " + '**IMPORTANT: Explore mode is for thinking, not implementing.** You may read files, search code, and investigate the codebase, but you must NEVER write code or implement features. If the user asks you '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-explore/SKILL.md')
    assert 'description: Enter explore mode - a thinking partner for exploring ideas, investigating problems, and clarifying requirements. Use when the user wants to think through something before or during a cha' in text, "expected to find: " + 'description: Enter explore mode - a thinking partner for exploring ideas, investigating problems, and clarifying requirements. Use when the user wants to think through something before or during a cha'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-explore/SKILL.md')
    assert "- **Open threads, not interrogations** - Surface multiple interesting directions and let the user follow what resonates. Don't funnel them through a single path of questions." in text, "expected to find: " + "- **Open threads, not interrogations** - Surface multiple interesting directions and let the user follow what resonates. Don't funnel them through a single path of questions."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-propose/SKILL.md')
    assert 'description: Propose a new change with all artifacts generated in one step. Use when the user wants to quickly describe what they want to build and get a complete proposal with design, specs, and task' in text, "expected to find: " + 'description: Propose a new change with all artifacts generated in one step. Use when the user wants to quickly describe what they want to build and get a complete proposal with design, specs, and task'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-propose/SKILL.md')
    assert "**Input**: The user's request should include a change name (kebab-case) OR a description of what they want to build." in text, "expected to find: " + "**Input**: The user's request should include a change name (kebab-case) OR a description of what they want to build."[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/openspec-propose/SKILL.md')
    assert '- If context is critically unclear, ask the user - but prefer making reasonable decisions to keep momentum' in text, "expected to find: " + '- If context is critically unclear, ask the user - but prefer making reasonable decisions to keep momentum'[:80]

