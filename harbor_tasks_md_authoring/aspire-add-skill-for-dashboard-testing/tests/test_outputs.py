"""Behavioral checks for aspire-add-skill-for-dashboard-testing (markdown_authoring task).

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
    assert 'Dashboard services require extensive DI setup (telemetry, storage, localization, FluentUI JS interop mocks, etc.). Reuse existing shared setup methods to avoid duplicate registration logic. **When add' in text, "expected to find: " + 'Dashboard services require extensive DI setup (telemetry, storage, localization, FluentUI JS interop mocks, etc.). Reuse existing shared setup methods to avoid duplicate registration logic. **When add'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dashboard-testing/SKILL.md')
    assert 'dotnet test tests/Aspire.Dashboard.Components.Tests/Aspire.Dashboard.Components.Tests.csproj -- --filter-method "*.UpdateResources_FiltersUpdated" --filter-not-trait "quarantined=true" --filter-not-tr' in text, "expected to find: " + 'dotnet test tests/Aspire.Dashboard.Components.Tests/Aspire.Dashboard.Components.Tests.csproj -- --filter-method "*.UpdateResources_FiltersUpdated" --filter-not-trait "quarantined=true" --filter-not-tr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/dashboard-testing/SKILL.md')
    assert '| `FluentUISetupHelpers.AddCommonDashboardServices()` | `Shared/FluentUISetupHelpers.cs` | Registers core DI services shared by all dashboard pages (localization, storage, telemetry, theme, dialog, sh' in text, "expected to find: " + '| `FluentUISetupHelpers.AddCommonDashboardServices()` | `Shared/FluentUISetupHelpers.cs` | Registers core DI services shared by all dashboard pages (localization, storage, telemetry, theme, dialog, sh'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **dashboard-testing**: Guide for writing tests for the Aspire Dashboard using xUnit and bUnit' in text, "expected to find: " + '- **dashboard-testing**: Guide for writing tests for the Aspire Dashboard using xUnit and bUnit'[:80]

