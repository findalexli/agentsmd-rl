"""Behavioral checks for backstage-feat-add-cursor-testing-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backstage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/backend-test-utils.mdc')
    assert '**CRITICAL**: When writing tests for Backstage backend code, you MUST use utilities from `@backstage/backend-test-utils` wherever possible. Do NOT create custom mocks, test databases, caches, or servi' in text, "expected to find: " + '**CRITICAL**: When writing tests for Backstage backend code, you MUST use utilities from `@backstage/backend-test-utils` wherever possible. Do NOT create custom mocks, test databases, caches, or servi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/backend-test-utils.mdc')
    assert '5. **Database Testing**: Always use `TestDatabases` from `@backstage/backend-test-utils` for database testing. This supports multiple database engines (PostgreSQL, MySQL, SQLite) and handles ephemeral' in text, "expected to find: " + '5. **Database Testing**: Always use `TestDatabases` from `@backstage/backend-test-utils` for database testing. This supports multiple database engines (PostgreSQL, MySQL, SQLite) and handles ephemeral'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/backend-test-utils.mdc')
    assert '6. **Cache Testing**: Always use `TestCaches` from `@backstage/backend-test-utils` for cache testing. This supports multiple cache backends (Redis, Valkey, Memcache) and handles ephemeral test cache c' in text, "expected to find: " + '6. **Cache Testing**: Always use `TestCaches` from `@backstage/backend-test-utils` for cache testing. This supports multiple cache backends (Redis, Valkey, Memcache) and handles ephemeral test cache c'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/test-utils.mdc')
    assert '**CRITICAL**: When writing tests for Backstage frontend code, plugins, or React components, you MUST use utilities from `@backstage/test-utils` wherever possible. Do NOT create custom mocks, test wrap' in text, "expected to find: " + '**CRITICAL**: When writing tests for Backstage frontend code, plugins, or React components, you MUST use utilities from `@backstage/test-utils` wherever possible. Do NOT create custom mocks, test wrap'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/test-utils.mdc')
    assert '2. **Test App Wrappers**: Always use `wrapInTestApp` or `renderInTestApp` from `@backstage/test-utils` when testing React components that need Backstage app context (routing, theme, APIs). Use `create' in text, "expected to find: " + '2. **Test App Wrappers**: Always use `wrapInTestApp` or `renderInTestApp` from `@backstage/test-utils` when testing React components that need Backstage app context (routing, theme, APIs). Use `create'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tests/test-utils.mdc')
    assert '4. **Async Component Rendering**: Use `renderWithEffects` from `@backstage/test-utils` when testing components that perform asynchronous operations (e.g., useEffect with fetch). This properly handles ' in text, "expected to find: " + '4. **Async Component Rendering**: Use `renderWithEffects` from `@backstage/test-utils` when testing components that perform asynchronous operations (e.g., useEffect with fetch). This properly handles '[:80]

