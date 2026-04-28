"""Behavioral checks for monorepo-add-agentsmd-files (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/monorepo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the InversifyJS monorepo - a TypeScript dependency injection library ecosystem. The repository contains multiple packages organized into categories:' in text, "expected to find: " + 'This is the InversifyJS monorepo - a TypeScript dependency injection library ecosystem. The repository contains multiple packages organized into categories:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Formatting**: Prettier configuration shared via `@inversifyjs/foundation-prettier-config`' in text, "expected to find: " + '- **Formatting**: Prettier configuration shared via `@inversifyjs/foundation-prettier-config`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **Clear naming**: Use descriptive test names with "when called, and [condition]" pattern' in text, "expected to find: " + '4. **Clear naming**: Use descriptive test names with "when called, and [condition]" pattern'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/examples/AGENTS.md')
    assert 'This directory contains example packages that demonstrate how to use the InversifyJS container libraries. These are **demonstration packages**, not libraries for consumption.' in text, "expected to find: " + 'This directory contains example packages that demonstrate how to use the InversifyJS container libraries. These are **demonstration packages**, not libraries for consumption.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/examples/AGENTS.md')
    assert '- **Dependencies on workspace packages** - examples use local workspace dependencies' in text, "expected to find: " + '- **Dependencies on workspace packages** - examples use local workspace dependencies'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/examples/AGENTS.md')
    assert '- **Demonstration code** - shows usage patterns, not library implementation' in text, "expected to find: " + '- **Demonstration code** - shows usage patterns, not library implementation'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/binding-decorators/AGENTS.md')
    assert 'The `@inversifyjs/binding-decorators` package provides decorator-based binding configuration for InversifyJS. It enables developers to configure dependency injection through TypeScript decorators, off' in text, "expected to find: " + 'The `@inversifyjs/binding-decorators` package provides decorator-based binding configuration for InversifyJS. It enables developers to configure dependency injection through TypeScript decorators, off'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/binding-decorators/AGENTS.md')
    assert '- **Reflection Integration**: Works with reflect-metadata for design-time type information' in text, "expected to find: " + '- **Reflection Integration**: Works with reflect-metadata for design-time type information'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/binding-decorators/AGENTS.md')
    assert '- **Metadata Management**: Stores and retrieves binding metadata from decorated classes' in text, "expected to find: " + '- **Metadata Management**: Stores and retrieves binding metadata from decorated classes'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/common/AGENTS.md')
    assert 'The `@inversifyjs/common` package provides shared utilities, types, and constants used across the entire InversifyJS container ecosystem. It serves as the foundation layer that other packages build up' in text, "expected to find: " + 'The `@inversifyjs/common` package provides shared utilities, types, and constants used across the entire InversifyJS container ecosystem. It serves as the foundation layer that other packages build up'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/common/AGENTS.md')
    assert 'Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):' in text, "expected to find: " + 'Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/common/AGENTS.md')
    assert '- **Dependencies**: Avoid adding new dependencies unless absolutely necessary' in text, "expected to find: " + '- **Dependencies**: Avoid adding new dependencies unless absolutely necessary'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/container/AGENTS.md')
    assert 'The `@inversifyjs/container` package provides the high-level container API and user-facing interfaces for the InversifyJS dependency injection system. It builds on `@inversifyjs/core` to provide a com' in text, "expected to find: " + 'The `@inversifyjs/container` package provides the high-level container API and user-facing interfaces for the InversifyJS dependency injection system. It builds on `@inversifyjs/core` to provide a com'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/container/AGENTS.md')
    assert '- Binding configuration is typically done at startup, so optimization focus is on resolution' in text, "expected to find: " + '- Binding configuration is typically done at startup, so optimization focus is on resolution'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/container/AGENTS.md')
    assert 'Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):' in text, "expected to find: " + 'Follow the [structured testing approach](../../../../docs/testing/unit-testing.md):'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/core/AGENTS.md')
    assert 'The `@inversifyjs/core` package is the foundational layer of the InversifyJS dependency injection system. It contains the core planning algorithms, resolution logic, and fundamental architecture patte' in text, "expected to find: " + 'The `@inversifyjs/core` package is the foundational layer of the InversifyJS dependency injection system. It contains the core planning algorithms, resolution logic, and fundamental architecture patte'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/core/AGENTS.md')
    assert 'Follow the [four-layer testing structure](../../../../docs/testing/unit-testing.md):' in text, "expected to find: " + 'Follow the [four-layer testing structure](../../../../docs/testing/unit-testing.md):'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/core/AGENTS.md')
    assert '- **Factory Pattern**: Different activation strategies for different binding types' in text, "expected to find: " + '- **Factory Pattern**: Different activation strategies for different binding types'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin-dispose/AGENTS.md')
    assert 'The `@inversifyjs/plugin-dispose` package provides automatic resource disposal and cleanup functionality for InversifyJS containers. It implements the plugin interface to add lifecycle management capa' in text, "expected to find: " + 'The `@inversifyjs/plugin-dispose` package provides automatic resource disposal and cleanup functionality for InversifyJS containers. It implements the plugin interface to add lifecycle management capa'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin-dispose/AGENTS.md')
    assert '- **Disposal Patterns**: Supports various disposal patterns (IDisposable, async disposal, etc.)' in text, "expected to find: " + '- **Disposal Patterns**: Supports various disposal patterns (IDisposable, async disposal, etc.)'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin-dispose/AGENTS.md')
    assert '- **Plugin Implementation**: Implements the plugin interface for container integration' in text, "expected to find: " + '- **Plugin Implementation**: Implements the plugin interface for container integration'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin/AGENTS.md')
    assert 'The `@inversifyjs/plugin` package provides the plugin system interface and base functionality for extending InversifyJS containers. It defines the plugin architecture that allows developers to add cus' in text, "expected to find: " + 'The `@inversifyjs/plugin` package provides the plugin system interface and base functionality for extending InversifyJS containers. It defines the plugin architecture that allows developers to add cus'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin/AGENTS.md')
    assert 'Note: This package typically does not have tests since it primarily provides interfaces.' in text, "expected to find: " + 'Note: This package typically does not have tests since it primarily provides interfaces.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/plugin/AGENTS.md')
    assert "- **No Tests**: This package typically has no test files since it's interface-only" in text, "expected to find: " + "- **No Tests**: This package typically has no test files since it's interface-only"[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/strongly-typed/AGENTS.md')
    assert 'The `@inversifyjs/strongly-typed` package provides enhanced type safety and compile-time guarantees for InversifyJS containers. It leverages advanced TypeScript features to ensure that dependency inje' in text, "expected to find: " + 'The `@inversifyjs/strongly-typed` package provides enhanced type safety and compile-time guarantees for InversifyJS containers. It leverages advanced TypeScript features to ensure that dependency inje'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/strongly-typed/AGENTS.md')
    assert 'export function createServiceIdentifier<T>(description?: string): ServiceIdentifier<T> {' in text, "expected to find: " + 'export function createServiceIdentifier<T>(description?: string): ServiceIdentifier<T> {'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/container/libraries/strongly-typed/AGENTS.md')
    assert '1. **Type Tests** (`*.spec-d.ts`): Test TypeScript type checking with `tsd` or similar' in text, "expected to find: " + '1. **Type Tests** (`*.spec-d.ts`): Test TypeScript type checking with `tsd` or similar'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/docs/tools/AGENTS.md')
    assert 'This directory contains code examples and tools for generating documentation examples. These packages demonstrate usage patterns for the InversifyJS ecosystem but **do not export library code**.' in text, "expected to find: " + 'This directory contains code examples and tools for generating documentation examples. These packages demonstrate usage patterns for the InversifyJS ecosystem but **do not export library code**.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/docs/tools/AGENTS.md')
    assert '- **Multiple InversifyJS versions**: Some packages depend on both `inversify@6.x` and `inversify7@7.x`' in text, "expected to find: " + '- **Multiple InversifyJS versions**: Some packages depend on both `inversify@6.x` and `inversify7@7.x`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/docs/tools/AGENTS.md')
    assert '- **No unit tests** - the code demonstrates usage, not library implementation' in text, "expected to find: " + '- **No unit tests** - the code demonstrates usage, not library implementation'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/foundation/tools/AGENTS.md')
    assert 'This directory contains shared foundation tooling packages that provide common configurations for ESLint, Prettier, TypeScript, Rollup, Vitest, and Stryker across the entire monorepo.' in text, "expected to find: " + 'This directory contains shared foundation tooling packages that provide common configurations for ESLint, Prettier, TypeScript, Rollup, Vitest, and Stryker across the entire monorepo.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/foundation/tools/AGENTS.md')
    assert '2. **TypeScript changes**: Run `pnpm run build` to verify compilation' in text, "expected to find: " + '2. **TypeScript changes**: Run `pnpm run build` to verify compilation'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/foundation/tools/AGENTS.md')
    assert '- **stryker-config**: Shared Stryker mutation testing configuration' in text, "expected to find: " + '- **stryker-config**: Shared Stryker mutation testing configuration'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/framework/core/AGENTS.md')
    assert 'This is the InversifyJS framework core package that provides foundational framework functionality and utilities for building applications with dependency injection.' in text, "expected to find: " + 'This is the InversifyJS framework core package that provides foundational framework functionality and utilities for building applications with dependency injection.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/framework/core/AGENTS.md')
    assert 'This package requires **comprehensive unit testing** following the [testing guidelines](../../docs/testing/unit-testing.md).' in text, "expected to find: " + 'This package requires **comprehensive unit testing** following the [testing guidelines](../../docs/testing/unit-testing.md).'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/framework/core/AGENTS.md')
    assert '- **Lifecycle management** - supports component initialization and cleanup' in text, "expected to find: " + '- **Lifecycle management** - supports component initialization and cleanup'[:80]

