"""Behavioral checks for insforge-ins68-enhance-skills-local-development (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/insforge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insforge-dev/dashboard/SKILL.md')
    assert 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be' in text, "expected to find: " + 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insforge-dev/dashboard/SKILL.md')
    assert "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI " in text, "expected to find: " + "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/insforge-dev/dashboard/SKILL.md')
    assert '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo' in text, "expected to find: " + '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/insforge-dev/dashboard/SKILL.md')
    assert 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be' in text, "expected to find: " + 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/insforge-dev/dashboard/SKILL.md')
    assert "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI " in text, "expected to find: " + "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI "[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/insforge-dev/dashboard/SKILL.md')
    assert '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo' in text, "expected to find: " + '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/insforge-dev/dashboard/SKILL.md')
    assert 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be' in text, "expected to find: " + 'The lowest-friction approach is to **temporarily hardcode** the three gates below to `true`/the new branch, then restart the Vite dev server. These edits bypass real host/project detection and MUST be'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/insforge-dev/dashboard/SKILL.md')
    assert "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI " in text, "expected to find: " + "**Use when** previewing UI gated on `useIsCloudHostingMode()`, `isInsForgeCloudProject()`, or a PostHog feature flag (e.g. the CTest dashboard variant, `dashboard-v3-experiment === 'c_test'`, the CLI "[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/insforge-dev/dashboard/SKILL.md')
    assert '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo' in text, "expected to find: " + '3. If the UI is also feature-flag-gated, hardcode the consumer. For CTest: `AppRoutes.tsx` → `const DashboardHomePage = CTestDashboardPage;` and, if relevant, the matching branch in `AppLayout.tsx` fo'[:80]

