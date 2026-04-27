"""Behavioral checks for biome-chore-add-eslintmigrateoptions-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/biome")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/README.md')
    assert '| **[eslint-migrate-options](./eslint-migrate-options/SKILL.md)** | Write custom ESLint-to-Biome option migrators | Any agent |' in text, "expected to find: " + '| **[eslint-migrate-options](./eslint-migrate-options/SKILL.md)** | Write custom ESLint-to-Biome option migrators | Any agent |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/README.md')
    assert '└── eslint-migrate-options/' in text, "expected to find: " + '└── eslint-migrate-options/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/README.md')
    assert '├── prettier-compare/' in text, "expected to find: " + '├── prettier-compare/'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/eslint-migrate-options/SKILL.md')
    assert 'description: Guide for implementing ESLint-to-Biome rule option migrators inside `biome migrate eslint`. Use whenever you add or update a Biome lint rule that has an ESLint source rule with configurab' in text, "expected to find: " + 'description: Guide for implementing ESLint-to-Biome rule option migrators inside `biome migrate eslint`. Use whenever you add or update a Biome lint rule that has an ESLint source rule with configurab'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/eslint-migrate-options/SKILL.md')
    assert 'Before writing anything new, find a nearby rule that already migrates options. Reuse its shape if the target rule is in the same plugin or has the same Biome configuration type (`RuleConfiguration` vs' in text, "expected to find: " + 'Before writing anything new, find a nearby rule that already migrates options. Reuse its shape if the target rule is in the same plugin or has the same Biome configuration type (`RuleConfiguration` vs'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/eslint-migrate-options/SKILL.md')
    assert 'If an ESLint option should only be emitted when at least one nested field is set, use a helper that returns `Option<_>` rather than constructing empty Biome option objects.' in text, "expected to find: " + 'If an ESLint option should only be emitted when at least one nested field is set, use a helper that returns `Option<_>` rather than constructing empty Biome option objects.'[:80]

