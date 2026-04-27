"""Behavioral checks for antigravity-awesome-skills-fix-correct-sourcerepo-field-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-expert/SKILL.md')
    assert 'Transform any codebase into an AI-intelligent project with persistent context that survives across sessions, tools, and AI platforms. Expert-level control over the foundational layer that powers moder' in text, "expected to find: " + 'Transform any codebase into an AI-intelligent project with persistent context that survives across sessions, tools, and AI platforms. Expert-level control over the foundational layer that powers moder'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-expert/SKILL.md')
    assert 'description: "Advanced .faf (Foundational AI-context Format) specialist. IANA-registered format, MCP server config, championship scoring, bi-directional sync."' in text, "expected to find: " + 'description: "Advanced .faf (Foundational AI-context Format) specialist. IANA-registered format, MCP server config, championship scoring, bi-directional sync."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-expert/SKILL.md')
    assert '*Master the format that makes AI understand your projects. FAF Expert - for when you need championship-grade AI context architecture.*' in text, "expected to find: " + '*Master the format that makes AI understand your projects. FAF Expert - for when you need championship-grade AI context architecture.*'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-wizard/SKILL.md')
    assert 'Transform any project - new, legacy, famous OSS, or forgotten side projects - into an AI-intelligent workspace with persistent context that works across all AI tools.' in text, "expected to find: " + 'Transform any project - new, legacy, famous OSS, or forgotten side projects - into an AI-intelligent workspace with persistent context that works across all AI tools.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-wizard/SKILL.md')
    assert 'description: "Done-for-you .faf generator. One-click AI context for any project - new, legacy, or famous. Auto-detects stack, scores readiness, works everywhere."' in text, "expected to find: " + 'description: "Done-for-you .faf generator. One-click AI context for any project - new, legacy, or famous. Auto-detects stack, scores readiness, works everywhere."'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/faf-wizard/SKILL.md')
    assert "Documentation tells humans how to use your code. AI context tells AI how to help you build it. **They're completely different things.**" in text, "expected to find: " + "Documentation tells humans how to use your code. AI context tells AI how to help you build it. **They're completely different things.**"[:80]

