"""Behavioral checks for aider-desk-improve-skill-descriptions-and-content (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aider-desk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/agent-creator/SKILL.md')
    assert 'description: Create and configure AiderDesk agent profiles by defining tool groups, approval rules, subagent settings, and provider/model selection. Use when setting up a new agent, creating a profile' in text, "expected to find: " + 'description: Create and configure AiderDesk agent profiles by defining tool groups, approval rules, subagent settings, and provider/model selection. Use when setting up a new agent, creating a profile'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/agent-creator/SKILL.md')
    assert 'On user confirmation, generate the profile. Verify structure against `references/profile-examples.md` before creating files.' in text, "expected to find: " + 'On user confirmation, generate the profile. Verify structure against `references/profile-examples.md` before creating files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/agent-creator/SKILL.md')
    assert '**Every agent is a subagent (enabled: true)**. See `references/subagent-guide.md` for detailed guidance.' in text, "expected to find: " + '**Every agent is a subagent (enabled: true)**. See `references/subagent-guide.md` for detailed guidance.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/skill-creator/SKILL.md')
    assert 'description: Create AiderDesk Agent Skills by writing SKILL.md files, defining frontmatter metadata, structuring references, and organizing skill directories. Use when building a new skill, creating a' in text, "expected to find: " + 'description: Create AiderDesk Agent Skills by writing SKILL.md files, defining frontmatter metadata, structuring references, and organizing skill directories. Use when building a new skill, creating a'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/skill-creator/SKILL.md')
    assert "**If skill doesn't load**: check YAML syntax is valid, `name` is lowercase-hyphenated, and `description` contains the trigger terms users would say" in text, "expected to find: " + "**If skill doesn't load**: check YAML syntax is valid, `name` is lowercase-hyphenated, and `description` contains the trigger terms users would say"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/skill-creator/SKILL.md')
    assert 'description: Deploy AiderDesk builds to staging and production environments. Use when deploying, releasing, or publishing builds.' in text, "expected to find: " + 'description: Deploy AiderDesk builds to staging and production environments. Use when deploying, releasing, or publishing builds.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/theme-factory/SKILL.md')
    assert 'description: Create new AiderDesk UI themes by defining SCSS color variables, registering theme types, and adding i18n display names. Use when adding a theme, creating a color scheme, customizing appe' in text, "expected to find: " + 'description: Create new AiderDesk UI themes by defining SCSS color variables, registering theme types, and adding i18n display names. Use when adding a theme, creating a color scheme, customizing appe'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/writing-tests/SKILL.md')
    assert 'description: Write unit tests, component tests, and integration tests for AiderDesk using Vitest and React Testing Library. Use when creating new tests, adding test coverage, configuring mocks, settin' in text, "expected to find: " + 'description: Write unit tests, component tests, and integration tests for AiderDesk using Vitest and React Testing Library. Use when creating new tests, adding test coverage, configuring mocks, settin'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/writing-tests/SKILL.md')
    assert '2. Check mock setup — verify `vi.mock()` paths and return values match expectations' in text, "expected to find: " + '2. Check mock setup — verify `vi.mock()` paths and return values match expectations'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.aider-desk/skills/writing-tests/SKILL.md')
    assert '4. Run a single test in isolation: `npm run test:node -- --no-color -t "test name"`' in text, "expected to find: " + '4. Run a single test in isolation: `npm run test:node -- --no-color -t "test name"`'[:80]

