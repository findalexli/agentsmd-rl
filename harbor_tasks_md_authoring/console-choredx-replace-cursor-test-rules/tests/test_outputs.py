"""Behavioral checks for console-choredx-replace-cursor-test-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/console")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/SKILL.md')
    assert 'description: "Write tests for the akash-network/console monorepo following established team patterns and reviewer expectations. Use this skill whenever you need to write, fix, review, or refactor test' in text, "expected to find: " + 'description: "Write tests for the akash-network/console monorepo following established team patterns and reviewer expectations. Use this skill whenever you need to write, fix, review, or refactor test'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/SKILL.md')
    assert "When testing error paths, focus on errors the code explicitly handles — but don't skip error coverage just because the happy path works. If a service catches and transforms errors, test those paths. I" in text, "expected to find: " + "When testing error paths, focus on errors the code explicitly handles — but don't skip error coverage just because the happy path works. If a service catches and transforms errors, test those paths. I"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/SKILL.md')
    assert 'Always use `mock<T>()` for typed mocks. Never use `jest.mock()` or `vi.mock()` for module-level mocking — it causes OOM with heavy component trees and couples tests to implementation details.' in text, "expected to find: " + 'Always use `mock<T>()` for typed mocks. Never use `jest.mock()` or `vi.mock()` for module-level mocking — it causes OOM with heavy component trees and couples tests to implementation details.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/api-patterns.md')
    assert "Functional tests use **whitebox seeding** and **blackbox testing**: seed data at the DB/repository level, but interact with the service only through HTTP. Don't resolve controllers or services from th" in text, "expected to find: " + "Functional tests use **whitebox seeding** and **blackbox testing**: seed data at the DB/repository level, but interact with the service only through HTTP. Don't resolve controllers or services from th"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/api-patterns.md')
    assert 'Use a plain HTTP client that makes real requests over the network. This decouples tests from the HTTP framework — if the app migrates from Hono to another framework, the tests survive unchanged.' in text, "expected to find: " + 'Use a plain HTTP client that makes real requests over the network. This decouples tests from the HTTP framework — if the app migrates from Hono to another framework, the tests survive unchanged.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/api-patterns.md')
    assert 'Construct the service under test manually, passing `vitest-mock-extended` mocks for all dependencies. Always use the `setup()` function at the bottom of the root `describe`.' in text, "expected to find: " + 'Construct the service under test manually, passing `vitest-mock-extended` mocks for all dependencies. Always use the `setup()` function at the bottom of the root `describe`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/frontend-patterns.md')
    assert 'This is the canonical pattern for testing React components without `vi.mock()`. Components export their heavy dependencies (child components, hooks, and any other heavy imports) and accept them as a p' in text, "expected to find: " + 'This is the canonical pattern for testing React components without `vi.mock()`. Components export their heavy dependencies (child components, hooks, and any other heavy imports) and accept them as a p'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/frontend-patterns.md')
    assert '**Important distinction**: Services should be injected via `useServices` hook (DI container), NOT via the `DEPENDENCIES` prop. The `DEPENDENCIES` prop is for components and hooks only.' in text, "expected to find: " + '**Important distinction**: Services should be injected via `useServices` hook (DI container), NOT via the `DEPENDENCIES` prop. The `DEPENDENCIES` prop is for components and hooks only.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/console-tests/references/frontend-patterns.md')
    assert 'Use the `setupQuery` utility from `apps/deploy-web/tests/unit/query-client.tsx`. It wraps `renderHook` with `TestContainerProvider` containing a `QueryClient` and mock services.' in text, "expected to find: " + 'Use the `setupQuery` utility from `apps/deploy-web/tests/unit/query-client.tsx`. It wraps `renderHook` with `TestContainerProvider` containing a `QueryClient` and mock services.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/no-jest-mock.mdc')
    assert '.cursor/rules/no-jest-mock.mdc' in text, "expected to find: " + '.cursor/rules/no-jest-mock.mdc'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/query-by-in-tests.mdc')
    assert '.cursor/rules/query-by-in-tests.mdc' in text, "expected to find: " + '.cursor/rules/query-by-in-tests.mdc'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/setup-instead-of-before-each.mdc')
    assert '.cursor/rules/setup-instead-of-before-each.mdc' in text, "expected to find: " + '.cursor/rules/setup-instead-of-before-each.mdc'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-descriptions.mdc')
    assert '.cursor/rules/test-descriptions.mdc' in text, "expected to find: " + '.cursor/rules/test-descriptions.mdc'[:80]

