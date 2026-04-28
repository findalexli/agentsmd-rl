"""Behavioral checks for arkenv-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/arkenv")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/arktype.mdc')
    assert "This project is built on [ArkType](https://arktype.io/), TypeScript's 1:1 validator." in text, "expected to find: " + "This project is built on [ArkType](https://arktype.io/), TypeScript's 1:1 validator."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/arktype.mdc')
    assert "Custom types are defined in `scope.ts` using ArkType's scoped type system:" in text, "expected to find: " + "Custom types are defined in `scope.ts` using ArkType's scoped type system:"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/arktype.mdc')
    assert '- Use the scoped `$` type system for custom types (see `scope.ts`)' in text, "expected to find: " + '- Use the scoped `$` type system for custom types (see `scope.ts`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert 'This project uses [Biome](https://biomejs.dev/) for formatting and linting. The configuration is in `biome.jsonc`.' in text, "expected to find: " + 'This project uses [Biome](https://biomejs.dev/) for formatting and linting. The configuration is in `biome.jsonc`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert '- **Single variable declarations**: Declare one variable per statement (`useSingleVarDeclarator` error)' in text, "expected to find: " + '- **Single variable declarations**: Declare one variable per statement (`useSingleVarDeclarator` error)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/coding-guidelines.mdc')
    assert '- **Type inference**: Avoid explicit types when TypeScript can infer them (`noInferrableTypes` error)' in text, "expected to find: " + '- **Type inference**: Avoid explicit types when TypeScript can infer them (`noInferrableTypes` error)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monorepo.mdc')
    assert '- `packages/arkenv` should not depend on other workspace packages' in text, "expected to find: " + '- `packages/arkenv` should not depend on other workspace packages'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monorepo.mdc')
    assert '├── tooling/          # Development tools (not published)' in text, "expected to find: " + '├── tooling/          # Development tools (not published)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/monorepo.mdc')
    assert 'Use Turborepo filters to run tasks on specific packages:' in text, "expected to find: " + 'Use Turborepo filters to run tasks on specific packages:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pnpm.mdc')
    assert 'Certain dependencies are configured to use `onlyBuiltDependencies` in `pnpm.onlyBuiltDependencies`. These are typically native dependencies that need special handling:' in text, "expected to find: " + 'Certain dependencies are configured to use `onlyBuiltDependencies` in `pnpm.onlyBuiltDependencies`. These are typically native dependencies that need special handling:'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pnpm.mdc')
    assert '- The project uses `pnpm@10.20.0` (specified in `packageManager` field)' in text, "expected to find: " + '- The project uses `pnpm@10.20.0` (specified in `packageManager` field)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pnpm.mdc')
    assert '- Run `pnpm install` to update the lock file when dependencies change' in text, "expected to find: " + '- Run `pnpm install` to update the lock file when dependencies change'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert '**Test behavior, not aesthetics.** Focus on what users can do and what the component guarantees through its API.' in text, "expected to find: " + '**Test behavior, not aesthetics.** Focus on what users can do and what the component guarantees through its API.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert '**"Test the User Journey"** - End-to-end tests validate complete user workflows in real applications.' in text, "expected to find: " + '**"Test the User Journey"** - End-to-end tests validate complete user workflows in real applications.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/test-patterns.mdc')
    assert '- Use **Testing Library** for component tests (with `user-event` for real user simulation)' in text, "expected to find: " + '- Use **Testing Library** for component tests (with `user-event` for real user simulation)'[:80]

