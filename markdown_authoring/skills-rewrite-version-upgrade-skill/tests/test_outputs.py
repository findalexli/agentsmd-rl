"""Behavioral checks for skills-rewrite-version-upgrade-skill (markdown_authoring task).

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
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert 'description: "Guides Qdrant version upgrades without downtime. Use when someone asks \'how to upgrade Qdrant\', \'is my version compatible\', \'rolling upgrade\', \'can I skip versions\', \'upgrade broke somet' in text, "expected to find: " + 'description: "Guides Qdrant version upgrades without downtime. Use when someone asks \'how to upgrade Qdrant\', \'is my version compatible\', \'rolling upgrade\', \'can I skip versions\', \'upgrade broke somet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert 'Compatibility is only guaranteed between consecutive minor versions. You must upgrade sequentially (1.15 to 1.16 to 1.17). Qdrant Cloud automates intermediate steps, self-hosted does not. Storage migr' in text, "expected to find: " + 'Compatibility is only guaranteed between consecutive minor versions. You must upgrade sequentially (1.15 to 1.16 to 1.17). Qdrant Cloud automates intermediate steps, self-hosted does not. Storage migr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/qdrant-version-upgrade/SKILL.md')
    assert '- Backward compatible one minor version (server 1.17 works with SDK 1.16, but only for 1.16 features) [Qdrant fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)' in text, "expected to find: " + '- Backward compatible one minor version (server 1.17 works with SDK 1.16, but only for 1.16 features) [Qdrant fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)'[:80]

