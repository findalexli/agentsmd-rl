"""Behavioral checks for claude-code-plugins-plus-skills-featnotionpack-rewrite-notio (markdown_authoring task).

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
    text = _read('plugins/saas-packs/notion-pack/skills/notion-enterprise-rbac/SKILL.md')
    assert 'Implement enterprise-grade access control for Notion integrations. This covers the full OAuth 2.0 authorization flow for public integrations (multi-tenant), per-workspace token storage with encryption' in text, "expected to find: " + 'Implement enterprise-grade access control for Notion integrations. This covers the full OAuth 2.0 authorization flow for public integrations (multi-tenant), per-workspace token storage with encryption'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-enterprise-rbac/SKILL.md')
    assert '- [Sharing and Permissions](https://developers.notion.com/docs/create-a-notion-integration#sharing-and-permissions) — page-level model' in text, "expected to find: " + '- [Sharing and Permissions](https://developers.notion.com/docs/create-a-notion-integration#sharing-and-permissions) — page-level model'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/notion-pack/skills/notion-enterprise-rbac/SKILL.md')
    assert '- [Notion Capabilities](https://developers.notion.com/docs/create-a-notion-integration#capabilities) — read/update/insert/delete' in text, "expected to find: " + '- [Notion Capabilities](https://developers.notion.com/docs/create-a-notion-integration#capabilities) — read/update/insert/delete'[:80]

