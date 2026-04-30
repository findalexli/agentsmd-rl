"""Behavioral checks for skills-add-figma-skills-to-curated (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert 'description: Connects Figma design components to code components using Code Connect. Use when user says "code connect", "connect this component to code", "connect Figma to code", "map this component",' in text, "expected to find: " + 'description: Connects Figma design components to code components using Code Connect. Use when user says "code connect", "connect this component to code", "connect Figma to code", "map this component",'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert "This skill helps you connect Figma design components to their corresponding code implementations using Figma's Code Connect feature. It analyzes the Figma design structure, searches your codebase for " in text, "expected to find: " + "This skill helps you connect Figma design components to their corresponding code implementations using Figma's Code Connect feature. It analyzes the Figma design structure, searches your codebase for "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert '**Solution:** Inspect the component file to verify the language (TypeScript, JavaScript) and framework (React, Vue, etc.). Update the parameters accordingly. For TypeScript React components, use `clie' in text, "expected to find: " + '**Solution:** Inspect the component file to verify the language (TypeScript, JavaScript) and framework (React, Vue, etc.). Update the parameters accordingly. For TypeScript React components, use `clie'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert 'description: Generates custom design system rules for the user\'s codebase. Use when user says "create design system rules", "generate rules for my project", "set up design rules", "customize design sy' in text, "expected to find: " + 'description: Generates custom design system rules for the user\'s codebase. Use when user says "create design system rules", "generate rules for my project", "set up design rules", "customize design sy'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert "This skill helps you generate custom design system rules tailored to your project's specific needs. These rules guide Codex to produce consistent, high-quality code when implementing Figma designs, en" in text, "expected to find: " + "This skill helps you generate custom design system rules tailored to your project's specific needs. These rules guide Codex to produce consistent, high-quality code when implementing Figma designs, en"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert 'Design system rules are project-level instructions that encode the "unwritten knowledge" of your codebase - the kind of expertise that experienced developers know and would pass on to new team members' in text, "expected to find: " + 'Design system rules are project-level instructions that encode the "unwritten knowledge" of your codebase - the kind of expertise that experienced developers know and would pass on to new team members'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert 'description: Translates Figma designs into production-ready code with 1:1 visual fidelity. Use when implementing UI from Figma files, when user mentions "implement design", "generate code", "implement' in text, "expected to find: " + 'description: Translates Figma designs into production-ready code with 1:1 visual fidelity. Use when implementing UI from Figma files, when user mentions "implement design", "generate code", "implement'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert 'This skill provides a structured workflow for translating Figma designs into production-ready code with pixel-perfect accuracy. It ensures consistent integration with the Figma MCP server, proper use ' in text, "expected to find: " + 'This skill provides a structured workflow for translating Figma designs into production-ready code with pixel-perfect accuracy. It ensures consistent integration with the Figma MCP server, proper use '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert '**Note:** Selection-based prompting only works with the `figma-desktop` MCP server. The remote server requires a link to a frame or layer to extract context. The user must have the Figma desktop app o' in text, "expected to find: " + '**Note:** Selection-based prompting only works with the `figma-desktop` MCP server. The remote server requires a link to a frame or layer to extract context. The user must have the Figma desktop app o'[:80]

