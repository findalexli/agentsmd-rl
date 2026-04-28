"""Behavioral checks for peloton-to-garmin-migrate-cursor-rules-to-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/peloton-to-garmin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/working-issue/SKILL.md')
    assert 'description: Starts work on an existing GitHub issue by fetching its details, creating the correct branch, writing the spec file, committing, and pushing — leaving the project in a ready-to-implement ' in text, "expected to find: " + 'description: Starts work on an existing GitHub issue by fetching its details, creating the correct branch, writing the spec file, committing, and pushing — leaving the project in a ready-to-implement '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/working-issue/SKILL.md')
    assert '**Before creating a new file**, scan `docs/specs/` for an existing spec that covers the same feature area. If one exists, add a new `## Capability: <short title>` section to it rather than creating a ' in text, "expected to find: " + '**Before creating a new file**, scan `docs/specs/` for an existing spec that covers the same feature area. If one exists, add a new `## Capability: <short title>` section to it rather than creating a '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/working-issue/SKILL.md')
    assert 'Read the issue fully — understand the problem statement, acceptance criteria, and any blocking relationships. If the issue is marked as blocked by another open issue, flag this to the user before cont' in text, "expected to find: " + 'Read the issue fully — understand the problem statement, acceptance criteria, and any blocking relationships. If the issue is marked as blocked by another open issue, flag this to the user before cont'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-development-patterns.mdc')
    assert '.cursor/rules/api-development-patterns.mdc' in text, "expected to find: " + '.cursor/rules/api-development-patterns.mdc'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/configuration-patterns.mdc')
    assert '.cursor/rules/configuration-patterns.mdc' in text, "expected to find: " + '.cursor/rules/configuration-patterns.mdc'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-workflow.mdc')
    assert '.cursor/rules/development-workflow.mdc' in text, "expected to find: " + '.cursor/rules/development-workflow.mdc'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/documentation-guide.mdc')
    assert '.cursor/rules/documentation-guide.mdc' in text, "expected to find: " + '.cursor/rules/documentation-guide.mdc'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/knowledge-base-maintenance.mdc')
    assert '.cursor/rules/knowledge-base-maintenance.mdc' in text, "expected to find: " + '.cursor/rules/knowledge-base-maintenance.mdc'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/knowledge-base-reference.mdc')
    assert '.cursor/rules/knowledge-base-reference.mdc' in text, "expected to find: " + '.cursor/rules/knowledge-base-reference.mdc'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-overview.mdc')
    assert '.cursor/rules/project-overview.mdc' in text, "expected to find: " + '.cursor/rules/project-overview.mdc'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/sync-service-patterns.mdc')
    assert '.cursor/rules/sync-service-patterns.mdc' in text, "expected to find: " + '.cursor/rules/sync-service-patterns.mdc'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing-requirements.mdc')
    assert '.cursor/rules/testing-requirements.mdc' in text, "expected to find: " + '.cursor/rules/testing-requirements.mdc'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ui-development.mdc')
    assert '.cursor/rules/ui-development.mdc' in text, "expected to find: " + '.cursor/rules/ui-development.mdc'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Refer to `.ai/knowledge-base/03-development-setup.md` for setup instructions and `.ai/knowledge-base/04-troubleshooting-guide.md` for configuration issues.' in text, "expected to find: " + 'Refer to `.ai/knowledge-base/03-development-setup.md` for setup instructions and `.ai/knowledge-base/04-troubleshooting-guide.md` for configuration issues.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '4. **Verify** — Build and all tests must pass before committing (see `/working-issue` for the full validation sequence)' in text, "expected to find: " + '4. **Verify** — Build and all tests must pass before committing (see `/working-issue` for the full validation sequence)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| New issues/solutions | `04-troubleshooting-guide.md` — add troubleshooting scenarios, update diagnostic procedures |' in text, "expected to find: " + '| New issues/solutions | `04-troubleshooting-guide.md` — add troubleshooting scenarios, update diagnostic procedures |'[:80]

