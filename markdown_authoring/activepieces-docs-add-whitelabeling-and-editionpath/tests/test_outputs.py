"""Behavioral checks for activepieces-docs-add-whitelabeling-and-editionpath (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/activepieces")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **All customer-facing UI must be white-labeled.** Sign-in/signup pages, email templates, logos, and any user-visible branding must use the platform's configured appearance (name, colors, logos) — ne" in text, "expected to find: " + "- **All customer-facing UI must be white-labeled.** Sign-in/signup pages, email templates, logos, and any user-visible branding must use the platform's configured appearance (name, colors, logos) — ne"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Appearance is edition-gated.** Community always uses the default theme. Cloud always applies custom branding. Enterprise requires `platform.plan.customAppearanceEnabled`. See `packages/server/api/' in text, "expected to find: " + '- **Appearance is edition-gated.** Community always uses the default theme. Cloud always applies custom branding. Enterprise requires `platform.plan.customAppearanceEnabled`. See `packages/server/api/'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Feature gating pattern:** Backend uses `platformMustHaveFeatureEnabled()` middleware (returns 402). Frontend uses `LockedFeatureGuard` component and `enabled: platform.plan.<flag>` on queries.' in text, "expected to find: " + '- **Feature gating pattern:** Backend uses `platformMustHaveFeatureEnabled()` middleware (returns 402). Frontend uses `LockedFeatureGuard` component and `enabled: platform.plan.<flag>` on queries.'[:80]

