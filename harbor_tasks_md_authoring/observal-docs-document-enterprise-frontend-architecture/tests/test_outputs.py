"""Behavioral checks for observal-docs-document-enterprise-frontend-architecture (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/observal")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert "**Future resource-based access control** will follow PostHog's annotation pattern: include `user_access_level` on every API response object. The API filters results by team membership; the frontend re" in text, "expected to find: " + "**Future resource-based access control** will follow PostHog's annotation pattern: include `user_access_level` on every API response object. The API filters results by team membership; the frontend re"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert '**Enterprise-only admin pages** (audit log viewer, diagnostics, SCIM config) should be regular pages in `web/src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise' in text, "expected to find: " + '**Enterprise-only admin pages** (audit log viewer, diagnostics, SCIM config) should be regular pages in `web/src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ee/AGENTS.md')
    assert 'This follows the industry-standard pattern (Langfuse, PostHog, Infisical, Lago all do this). The `ee/` boundary is for backend licensing — the frontend is AGPL and gates features server-side, not by d' in text, "expected to find: " + 'This follows the industry-standard pattern (Langfuse, PostHog, Infisical, Lago all do this). The `ee/` boundary is for backend licensing — the frontend is AGPL and gates features server-side, not by d'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert 'There is NO `web/ee/` directory. Enterprise frontend code lives here in `web/src/`, gated server-side via `useDeploymentConfig()`. This follows the Langfuse/PostHog/Infisical pattern — the `ee/` bound' in text, "expected to find: " + 'There is NO `web/ee/` directory. Enterprise frontend code lives here in `web/src/`, gated server-side via `useDeploymentConfig()`. This follows the Langfuse/PostHog/Infisical pattern — the `ee/` bound'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert "**Pattern for new enterprise pages:** Add regular pages in `src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise. Don't duplicate pages or create separate direct" in text, "expected to find: " + "**Pattern for new enterprise pages:** Add regular pages in `src/app/(admin)/` that check deployment mode and show an upgrade prompt when not enterprise. Don't duplicate pages or create separate direct"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('web/AGENTS.md')
    assert '**Future resource-based access control:** API will include `user_access_level` on response objects (PostHog annotation pattern). Frontend reads the annotation — no client-side policy engine needed.' in text, "expected to find: " + '**Future resource-based access control:** API will include `user_access_level` on response objects (PostHog annotation pattern). Frontend reads the annotation — no client-side policy engine needed.'[:80]

