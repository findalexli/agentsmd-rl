"""Behavioral checks for scalar-feat-migrate-cursor-rules-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scalar")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cloud-agents-starter/SKILL.md')
    assert 'description: Minimal starter runbook for cloud agents to install dependencies, run packages, execute tests, and troubleshoot the Scalar monorepo quickly.' in text, "expected to find: " + 'description: Minimal starter runbook for cloud agents to install dependencies, run packages, execute tests, and troubleshoot the Scalar monorepo quickly.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cloud-agents-starter/SKILL.md')
    assert 'Preferred location for this skill: `.agents/skills/cloud-agents-starter/SKILL.md`.' in text, "expected to find: " + 'Preferred location for this skill: `.agents/skills/cloud-agents-starter/SKILL.md`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cloud-agents-starter/SKILL.md')
    assert 'name: cloud-agents-starter' in text, "expected to find: " + 'name: cloud-agents-starter'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/openapi-glossary/SKILL.md')
    assert 'description: Use consistent OpenAPI terminology and definitions when writing documentation, educational material, and tooling guidance.' in text, "expected to find: " + 'description: Use consistent OpenAPI terminology and definitions when writing documentation, educational material, and tooling guidance.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/openapi-glossary/SKILL.md')
    assert 'Now, the word "Swagger" is just part of the SwaggerHub brand of tooling. The specification is "OpenAPI" (not OpenAPI/Swagger).' in text, "expected to find: " + 'Now, the word "Swagger" is just part of the SwaggerHub brand of tooling. The specification is "OpenAPI" (not OpenAPI/Swagger).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/openapi-glossary/SKILL.md')
    assert 'name: openapi-glossary' in text, "expected to find: " + 'name: openapi-glossary'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tests/SKILL.md')
    assert 'description: Write clear, maintainable Vitest and Playwright tests with precise assertions, consistent structure, and strong behavioral coverage.' in text, "expected to find: " + 'description: Write clear, maintainable Vitest and Playwright tests with precise assertions, consistent structure, and strong behavioral coverage.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/typescript/SKILL.md')
    assert 'description: Write clear, predictable TypeScript and Vue TypeScript code with strong typing, maintainability, and consistent documentation conventions.' in text, "expected to find: " + 'description: Write clear, predictable TypeScript and Vue TypeScript code with strong typing, maintainability, and consistent documentation conventions.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/typescript/SKILL.md')
    assert 'name: typescript' in text, "expected to find: " + 'name: typescript'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vue-components/SKILL.md')
    assert 'description: Build Vue 3 components with TypeScript and Tailwind using clean structure, composable logic, accessibility, and maintainable patterns.' in text, "expected to find: " + 'description: Build Vue 3 components with TypeScript and Tailwind using clean structure, composable logic, accessibility, and maintainable patterns.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/vue-components/SKILL.md')
    assert 'name: vue-components' in text, "expected to find: " + 'name: vue-components'[:80]

