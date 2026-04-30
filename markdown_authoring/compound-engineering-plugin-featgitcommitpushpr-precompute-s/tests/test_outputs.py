"""Behavioral checks for compound-engineering-plugin-featgitcommitpushpr-precompute-s (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '- [ ] PR description includes Compound Engineered badge with accurate model and harness' in text, "expected to find: " + '- [ ] PR description includes Compound Engineered badge with accurate model and harness'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '- [ ] PR description includes Compound Engineered badge with accurate model and harness' in text, "expected to find: " + '- [ ] PR description includes Compound Engineered badge with accurate model and harness'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'If the line above resolved to a semantic version (e.g., `2.42.0`), use it as `[VERSION]` in the versioned badge below. Otherwise (empty, a literal command string, or an error), use the versionless bad' in text, "expected to find: " + 'If the line above resolved to a semantic version (e.g., `2.42.0`), use it as `[VERSION]` in the versioned badge below. Otherwise (empty, a literal command string, or an error), use the versionless bad'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '[![Compound Engineering](https://img.shields.io/badge/Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)' in text, "expected to find: " + '[![Compound Engineering](https://img.shields.io/badge/Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '**Plugin version (pre-resolved):** !`jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"`' in text, "expected to find: " + '**Plugin version (pre-resolved):** !`jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"`'[:80]

