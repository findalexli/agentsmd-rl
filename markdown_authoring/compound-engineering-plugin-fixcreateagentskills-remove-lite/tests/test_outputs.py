"""Behavioral checks for compound-engineering-plugin-fixcreateagentskills-remove-lite (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/create-agent-skills/SKILL.md')
    assert '**Important:** The preprocessor scans the entire SKILL.md as plain text — it does not parse markdown. Directives inside fenced code blocks or inline code spans are still executed. If a skill documents' in text, "expected to find: " + '**Important:** The preprocessor scans the entire SKILL.md as plain text — it does not parse markdown. Directives inside fenced code blocks or inline code spans are still executed. If a skill documents'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/create-agent-skills/SKILL.md')
    assert 'Skills support dynamic context injection: prefix a backtick-wrapped shell command with an exclamation mark, and the preprocessor executes it at load time, replacing the directive with stdout. Write an' in text, "expected to find: " + 'Skills support dynamic context injection: prefix a backtick-wrapped shell command with an exclamation mark, and the preprocessor executes it at load time, replacing the directive with stdout. Write an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/create-agent-skills/SKILL.md')
    assert 'For a concrete example of dynamic context injection in a skill, see [official-spec.md](references/official-spec.md) § "Dynamic Context Injection".' in text, "expected to find: " + 'For a concrete example of dynamic context injection in a skill, see [official-spec.md](references/official-spec.md) § "Dynamic Context Injection".'[:80]

