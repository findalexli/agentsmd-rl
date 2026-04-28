"""Behavioral checks for trpc-chore-add-some-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/trpc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert 'You are working on **tRPC** - a TypeScript-first RPC library that provides end-to-end type safety between client and server. As a TypeScript expert contributing to this library, you should:' in text, "expected to find: " + 'You are working on **tRPC** - a TypeScript-first RPC library that provides end-to-end type safety between client and server. As a TypeScript expert contributing to this library, you should:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert 'This codebase pushes TypeScript to its limits to provide seamless type safety across network boundaries. Every type decision impacts thousands of developers using tRPC in production.' in text, "expected to find: " + 'This codebase pushes TypeScript to its limits to provide seamless type safety across network boundaries. Every type decision impacts thousands of developers using tRPC in production.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert '- Understand advanced TypeScript concepts including conditional types, mapped types, and template literal types' in text, "expected to find: " + '- Understand advanced TypeScript concepts including conditional types, mapped types, and template literal types'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-query-tests.mdc')
    assert '- **ALWAYS** import `createAppRouter` from `./__testHelpers` (note the different filename from other packages)' in text, "expected to find: " + '- **ALWAYS** import `createAppRouter` from `./__testHelpers` (note the different filename from other packages)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-query-tests.mdc')
    assert '- Import from `./__testHelpers` or create inline router with `testServerAndClientResource`' in text, "expected to find: " + '- Import from `./__testHelpers` or create inline router with `testServerAndClientResource`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-query-tests.mdc')
    assert '- **Alternative**: Import `testServerAndClientResource` directly and create inline router' in text, "expected to find: " + '- **Alternative**: Import `testServerAndClientResource` directly and create inline router'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tanstack-react-query-tests.mdc')
    assert '- **ALWAYS** import `testReactResource` from `./__helpers` (local to tanstack-react-query package)' in text, "expected to find: " + '- **ALWAYS** import `testReactResource` from `./__helpers` (local to tanstack-react-query package)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tanstack-react-query-tests.mdc')
    assert "- **NEVER** import from other packages' helpers - each package has its own implementation" in text, "expected to find: " + "- **NEVER** import from other packages' helpers - each package has its own implementation"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/tanstack-react-query-tests.mdc')
    assert '- **ALWAYS** use `await using ctx = testReactResource()` for TanStack React Query tests' in text, "expected to find: " + '- **ALWAYS** use `await using ctx = testReactResource()` for TanStack React Query tests'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert '- **ALWAYS** use `await using ctx = testServerAndClientResource()` for tests that need both server and client setup' in text, "expected to find: " + '- **ALWAYS** use `await using ctx = testServerAndClientResource()` for tests that need both server and client setup'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert "- **NEVER** use the deprecated `routerToServerAndClientNew()` function - it's marked as deprecated" in text, "expected to find: " + "- **NEVER** use the deprecated `routerToServerAndClientNew()` function - it's marked as deprecated"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert '- Use the `testServerAndClientResource` import from `@trpc/client/__tests__/testClientResource`' in text, "expected to find: " + '- Use the `testServerAndClientResource` import from `@trpc/client/__tests__/testClientResource`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/upgrade-tests.mdc')
    assert '- **ALWAYS** import `testReactResource` from `./test/__helpers` (note the `test/` prefix)' in text, "expected to find: " + '- **ALWAYS** import `testReactResource` from `./test/__helpers` (note the `test/` prefix)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/upgrade-tests.mdc')
    assert "import { testReactResource } from './__helpers';      // TanStack only (different impl)" in text, "expected to find: " + "import { testReactResource } from './__helpers';      // TanStack only (different impl)"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/upgrade-tests.mdc')
    assert '- Uses nested providers: `QueryClientProvider` > `baseProxy.Provider` > `TRPCProvider`' in text, "expected to find: " + '- Uses nested providers: `QueryClientProvider` > `baseProxy.Provider` > `TRPCProvider`'[:80]

