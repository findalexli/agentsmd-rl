"""Behavioral checks for studio-add-some-new-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-development.mdc')
    assert "**Prefer Drizzle ORM for all new code.** We're gradually migrating away from Supabase queries:" in text, "expected to find: " + "**Prefer Drizzle ORM for all new code.** We're gradually migrating away from Supabase queries:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-development.mdc')
    assert 'For org-level operations, auto-resolve context and use slug-based authorization:' in text, "expected to find: " + 'For org-level operations, auto-resolve context and use slug-based authorization:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-development.mdc')
    assert '- Always use **org slug** for `assertTeamResourceAccess`, never numeric ID' in text, "expected to find: " + '- Always use **org slug** for `assertTeamResourceAccess`, never numeric ID'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data-flow.mdc')
    assert 'Tool groups automatically become virtual integrations accessible via `i:{group-name}`:' in text, "expected to find: " + 'Tool groups automatically become virtual integrations accessible via `i:{group-name}`:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data-flow.mdc')
    assert '- Return objects, not nullable primitives (MCP requirement)' in text, "expected to find: " + '- Return objects, not nullable primitives (MCP requirement)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/data-flow.mdc')
    assert 'const { data: tools } = useTools(integration.connection);' in text, "expected to find: " + 'const { data: tools } = useTools(integration.connection);'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/native-apps-and-views.mdc')
    assert 'This guide covers the complete pattern for adding new native applications to deco CMS, from MCP tools to frontend views with AI chat integration.' in text, "expected to find: " + 'This guide covers the complete pattern for adding new native applications to deco CMS, from MCP tools to frontend views with AI chat integration.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/native-apps-and-views.mdc')
    assert '`Use SETTING_UPDATE_ORG to update settings. Do NOT pass orgId - it will be auto-determined from context.`,' in text, "expected to find: " + '`Use SETTING_UPDATE_ORG to update settings. Do NOT pass orgId - it will be auto-determined from context.`,'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/native-apps-and-views.mdc')
    assert 'This follows all patterns and demonstrates real-world usage of native apps with full AI chat integration.' in text, "expected to find: " + 'This follows all patterns and demonstrates real-world usage of native apps with full AI chat integration.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-ts.mdc')
    assert 'For features that manipulate CSS or DOM directly (like theme editors, live previews):' in text, "expected to find: " + 'For features that manipulate CSS or DOM directly (like theme editors, live previews):'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-ts.mdc')
    assert 'import { useSetThreadContextEffect } from "../decopilot/thread-context-provider.tsx";' in text, "expected to find: " + 'import { useSetThreadContextEffect } from "../decopilot/thread-context-provider.tsx";'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-ts.mdc')
    assert 'Implement single-level undo that reverts to the **saved state**, not the -1 change:' in text, "expected to find: " + 'Implement single-level undo that reverts to the **saved state**, not the -1 change:'[:80]

