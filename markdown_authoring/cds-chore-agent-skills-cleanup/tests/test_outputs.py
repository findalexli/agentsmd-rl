"""Behavioral checks for cds-chore-agent-skills-cleanup (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cds")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/design-system-researcher.md')
    assert "- Use the `git.repo-manager` skill (`.claude/skills/git.repo-manager/SKILL.md`) to ensure the project's repository is cloned and up to date in `temp/repo-cache/`." in text, "expected to find: " + "- Use the `git.repo-manager` skill (`.claude/skills/git.repo-manager/SKILL.md`) to ensure the project's repository is cloned and up to date in `temp/repo-cache/`."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/code-review/SKILL.md')
    assert '.claude/skills/code-review/SKILL.md' in text, "expected to find: " + '.claude/skills/code-review/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.best-practices/SKILL.md')
    assert 'description: Use this skill whenever working on CDS React components in any package.' in text, "expected to find: " + 'description: Use this skill whenever working on CDS React components in any package.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.best-practices/SKILL.md')
    assert 'name: components.best-practices' in text, "expected to find: " + 'name: components.best-practices'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/README.md')
    assert '**Usage:** `/components.styles <ComponentName> [additional context]`' in text, "expected to find: " + '**Usage:** `/components.styles <ComponentName> [additional context]`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/README.md')
    assert '- `/components.styles Button add static classnames for sub elements`' in text, "expected to find: " + '- `/components.styles Button add static classnames for sub elements`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/README.md')
    assert 'This skill may be invoked by the user following the examples below.' in text, "expected to find: " + 'This skill may be invoked by the user following the examples below.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/SKILL.md')
    assert 'description: Guidelines writing styles API (styles, classNames, and static classNames) for a CDS component. Use this skill when adding customization options to a React component via `styles` or `class' in text, "expected to find: " + 'description: Guidelines writing styles API (styles, classNames, and static classNames) for a CDS component. Use this skill when adding customization options to a React component via `styles` or `class'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/SKILL.md')
    assert 'Goal: Add styles API (styles, classNames, and static classNames) to a CDS component and/or update the component documentation with styles documentation.' in text, "expected to find: " + 'Goal: Add styles API (styles, classNames, and static classNames) to a CDS component and/or update the component documentation with styles documentation.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.styles/SKILL.md')
    assert '2. **Create or update the styles documentation** use the `components.write-docs` SKILL for general knowledge on how to write component documentation:' in text, "expected to find: " + '2. **Create or update the styles documentation** use the `components.write-docs` SKILL for general knowledge on how to write component documentation:'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/README.md')
    assert '- `/component-docs LineChart add examples for real-time data updates`' in text, "expected to find: " + '- `/component-docs LineChart add examples for real-time data updates`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/README.md')
    assert 'This skill may be invoked by the user following the examples below.' in text, "expected to find: " + 'This skill may be invoked by the user following the examples below.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/README.md')
    assert '**Usage:** `/component-docs <ComponentName> [additional context]`' in text, "expected to find: " + '**Usage:** `/component-docs <ComponentName> [additional context]`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/SKILL.md')
    assert 'description: Guidelines for creating or updating documentation for a CDS component on the docsite (apps/docs/). Use this skill after creating or making updates to a CDS React component to write high q' in text, "expected to find: " + 'description: Guidelines for creating or updating documentation for a CDS component on the docsite (apps/docs/). Use this skill after creating or making updates to a CDS React component to write high q'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/SKILL.md')
    assert '- **Design tokens** - Use the `components.best-practices` SKILL for knowledge on valid CDS design token values (Color, Space, BorderRadius, Font, etc.)' in text, "expected to find: " + '- **Design tokens** - Use the `components.best-practices` SKILL for knowledge on valid CDS design token values (Color, Space, BorderRadius, Font, etc.)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/components.write-docs/SKILL.md')
    assert 'Goal: Create or update documentation for a CDS component on the docsite (apps/docs/).' in text, "expected to find: " + 'Goal: Create or update documentation for a CDS component on the docsite (apps/docs/).'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/dev.cds-mobile/SKILL.md')
    assert 'name: dev.cds-mobile' in text, "expected to find: " + 'name: dev.cds-mobile'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/dev.cds-web/SKILL.md')
    assert 'name: dev.cds-web' in text, "expected to find: " + 'name: dev.cds-web'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/feature-planner/SKILL.md')
    assert '.claude/skills/feature-planner/SKILL.md' in text, "expected to find: " + '.claude/skills/feature-planner/SKILL.md'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/figma.audit-connect/SKILL.md')
    assert '- **ALWAYS** reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL' in text, "expected to find: " + '- **ALWAYS** reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/figma.connect-best-practices/SKILL.md')
    assert 'description: Guidelines for writing Figma Code Connect property mappings. Use this skill when working on Figma Code Connect files, which typically end in .figma.tsx.' in text, "expected to find: " + 'description: Guidelines for writing Figma Code Connect property mappings. Use this skill when working on Figma Code Connect files, which typically end in .figma.tsx.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/figma.connect-best-practices/SKILL.md')
    assert 'name: figma.connect-best-practices' in text, "expected to find: " + 'name: figma.connect-best-practices'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/figma.create-connect/SKILL.md')
    assert '- ALWAYS reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL' in text, "expected to find: " + '- ALWAYS reference the guidelines for writing code connect mappings in the `figma.connect-best-practices` SKILL'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git.detect-breaking-changes/SKILL.md')
    assert 'description: Analyzes the previous N commits for breaking changes across the CDS public API surface. Use this skill when you need to check if any recent changes will cause breaking changes in the CDS ' in text, "expected to find: " + 'description: Analyzes the previous N commits for breaking changes across the CDS public API surface. Use this skill when you need to check if any recent changes will cause breaking changes in the CDS '[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git.detect-breaking-changes/SKILL.md')
    assert 'name: git.detect-breaking-changes' in text, "expected to find: " + 'name: git.detect-breaking-changes'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git.repo-manager/SKILL.md')
    assert 'name: git.repo-manager' in text, "expected to find: " + 'name: git.repo-manager'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research.component-libs/SKILL.md')
    assert 'name: research.component-libs' in text, "expected to find: " + 'name: research.component-libs'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research.deprecation-usage/SKILL.md')
    assert "If you are researching a single deprecation, find it in this monorepo's source code (DO NOT USE SOURCEGRAPH). It will be marked with the jsdoc `@deprecated` annotation. Inspect the code around the dep" in text, "expected to find: " + "If you are researching a single deprecation, find it in this monorepo's source code (DO NOT USE SOURCEGRAPH). It will be marked with the jsdoc `@deprecated` annotation. Inspect the code around the dep"[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research.deprecation-usage/SKILL.md')
    assert '`https://sourcegraph.cbhq.net/search?q=NOT+repo%3Afrontend%2Fcds%28-%28internal%7Cpublic%7Cnext%29%29%3F%24+file%3A..%28t%7Cj%29sx%3F%24+%3C%5Cs*CellMedia%5Cb%5B%5E%3E%5D*%3F%5Cs%2Btitle%5B%5Cs%3D%2F%' in text, "expected to find: " + '`https://sourcegraph.cbhq.net/search?q=NOT+repo%3Afrontend%2Fcds%28-%28internal%7Cpublic%7Cnext%29%29%3F%24+file%3A..%28t%7Cj%29sx%3F%24+%3C%5Cs*CellMedia%5Cb%5B%5E%3E%5D*%3F%5Cs%2Btitle%5B%5Cs%3D%2F%'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/research.deprecation-usage/SKILL.md')
    assert 'Your objective is to provide information to user about the extent to which deprecated members of CDS are used in customer repositories. This information should be as accurate as possible as it will be' in text, "expected to find: " + 'Your objective is to provide information to user about the extent to which deprecated members of CDS are used in customer repositories. This information should be as accurate as possible as it will be'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/summarize-commits/SKILL.md')
    assert '.claude/skills/summarize-commits/SKILL.md' in text, "expected to find: " + '.claude/skills/summarize-commits/SKILL.md'[:80]

