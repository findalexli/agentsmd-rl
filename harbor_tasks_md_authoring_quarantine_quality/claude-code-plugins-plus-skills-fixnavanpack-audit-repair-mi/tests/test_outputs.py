"""Behavioral checks for claude-code-plugins-plus-skills-fixnavanpack-audit-repair-mi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-debug-bundle/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-incident-runbook/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-migration-deep-dive/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md')
    assert '| Missing env vars | N/A | Config loader throws on startup; check the correct `.env.<environment>` file exists |' in text, "expected to find: " + '| Missing env vars | N/A | Config loader throws on startup; check the correct `.env.<environment>` file exists |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-multi-env-setup/SKILL.md')
    assert '| Wrong environment loaded | N/A | Verify NODE_ENV matches the intended `.env.<environment>` file |' in text, "expected to find: " + '| Wrong environment loaded | N/A | Verify NODE_ENV matches the intended `.env.<environment>` file |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-prod-checklist/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-reference-architecture/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md')
    assert 'plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md' in text, "expected to find: " + 'plugins/saas-packs/navan-pack/skills/navan-upgrade-migration/SKILL.md'[:80]

