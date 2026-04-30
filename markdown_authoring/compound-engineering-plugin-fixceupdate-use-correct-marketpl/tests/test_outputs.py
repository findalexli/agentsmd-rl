"""Behavioral checks for compound-engineering-plugin-fixceupdate-use-correct-marketpl (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert '!`gh release list --repo EveryInc/compound-engineering-plugin --limit 30 --json tagName --jq \'[.[] | select(.tagName | startswith("compound-engineering-v"))][0].tagName | sub("compound-engineering-v";' in text, "expected to find: " + '!`gh release list --repo EveryInc/compound-engineering-plugin --limit 30 --json tagName --jq \'[.[] | select(.tagName | startswith("compound-engineering-v"))][0].tagName | sub("compound-engineering-v";'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert '!`ls "${CLAUDE_PLUGIN_ROOT}/cache/compound-engineering-plugin/compound-engineering/" 2>/dev/null || echo \'__CE_UPDATE_CACHE_FAILED__\'`' in text, "expected to find: " + '!`ls "${CLAUDE_PLUGIN_ROOT}/cache/compound-engineering-plugin/compound-engineering/" 2>/dev/null || echo \'__CE_UPDATE_CACHE_FAILED__\'`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-update/SKILL.md')
    assert 'rm -rf "<plugin-root-path>/cache/compound-engineering-plugin/compound-engineering"' in text, "expected to find: " + 'rm -rf "<plugin-root-path>/cache/compound-engineering-plugin/compound-engineering"'[:80]

