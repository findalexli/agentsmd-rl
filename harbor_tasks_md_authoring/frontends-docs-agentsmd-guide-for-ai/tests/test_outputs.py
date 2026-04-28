"""Behavioral checks for frontends-docs-agentsmd-guide-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/frontends")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Shopware Frontends is a Vue.js framework for building custom eCommerce storefronts with Shopware 6. It's a pnpm workspace monorepo using Turbo for build orchestration." in text, "expected to find: " + "Shopware Frontends is a Vue.js framework for building custom eCommerce storefronts with Shopware 6. It's a pnpm workspace monorepo using Turbo for build orchestration."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [api-types/storeApiTypes.d.ts](packages/api-client/api-types/storeApiTypes.d.ts) - Generated Store API types' in text, "expected to find: " + '- [api-types/storeApiTypes.d.ts](packages/api-client/api-types/storeApiTypes.d.ts) - Generated Store API types'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [api-types/adminApiTypes.d.ts](packages/api-client/api-types/adminApiTypes.d.ts) - Generated Admin API types' in text, "expected to find: " + '- [api-types/adminApiTypes.d.ts](packages/api-client/api-types/adminApiTypes.d.ts) - Generated Admin API types'[:80]

