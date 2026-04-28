"""Behavioral checks for mirascope-chore-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mirascope")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Read existing implementations first**: Always examine similar existing code before implementing new features. For example, look at how `Projects` is implemented before implementing `Environments`' in text, "expected to find: " + '1. **Read existing implementations first**: Always examine similar existing code before implementing new features. For example, look at how `Projects` is implemented before implementing `Environments`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Understand the path parameter pattern**: The codebase uses REST-style path patterns (`"organizations/:organizationId/projects/:projectId"`) that determine authorization scope and type safety.' in text, "expected to find: " + '2. **Understand the path parameter pattern**: The codebase uses REST-style path patterns (`"organizations/:organizationId/projects/:projectId"`) that determine authorization scope and type safety.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Use appropriate fixtures**: `TestEffectOrganizationFixture` < `TestEffectProjectFixture` < `TestEffectEnvironmentFixture`. Each includes users with different role levels.' in text, "expected to find: " + '1. **Use appropriate fixtures**: `TestEffectOrganizationFixture` < `TestEffectProjectFixture` < `TestEffectEnvironmentFixture`. Each includes users with different role levels.'[:80]

