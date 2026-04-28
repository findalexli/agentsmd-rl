"""Behavioral checks for aspire-review-feedback-on-dashboard-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aspire")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dashboard-testing/SKILL.md')
    assert 'Both test projects use hand-rolled fakes — no mocking framework is used. Cross-project fakes live in `tests/Shared/` (e.g., `TestDashboardClient`, `ModelTestHelpers`), while bUnit-specific fakes live ' in text, "expected to find: " + 'Both test projects use hand-rolled fakes — no mocking framework is used. Cross-project fakes live in `tests/Shared/` (e.g., `TestDashboardClient`, `ModelTestHelpers`), while bUnit-specific fakes live '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dashboard-testing/SKILL.md')
    assert 'Apply `[UseCulture("en-US")]` to bUnit test classes that assert culture-sensitive formatting (for example, numbers or dates) so those tests run deterministically across environments:' in text, "expected to find: " + 'Apply `[UseCulture("en-US")]` to bUnit test classes that assert culture-sensitive formatting (for example, numbers or dates) so those tests run deterministically across environments:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dashboard-testing/SKILL.md')
    assert 'ModelTestHelpers.CreateResource(resourceName: "Resource1", resourceType: "Type1", state: KnownResourceState.Running),' in text, "expected to find: " + 'ModelTestHelpers.CreateResource(resourceName: "Resource1", resourceType: "Type1", state: KnownResourceState.Running),'[:80]

