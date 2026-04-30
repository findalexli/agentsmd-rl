"""Behavioral checks for ship-add-general-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ship")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/code-quality.mdc')
    assert 'Shared Prettier config in [packages/prettier-config/index.js](mdc:packages/prettier-config/index.js)' in text, "expected to find: " + 'Shared Prettier config in [packages/prettier-config/index.js](mdc:packages/prettier-config/index.js)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/code-quality.mdc')
    assert 'Shared ESLint configuration in [packages/eslint-config/](mdc:packages/eslint-config/):' in text, "expected to find: " + 'Shared ESLint configuration in [packages/eslint-config/](mdc:packages/eslint-config/):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/code-quality.mdc')
    assert 'After implementing a feature, run ESLint to automatically sort and organize imports:' in text, "expected to find: " + 'After implementing a feature, run ESLint to automatically sort and organize imports:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/package-management.mdc')
    assert 'description: Guidelines for pnpm workspace management, installing packages and workspace dependencies' in text, "expected to find: " + 'description: Guidelines for pnpm workspace management, installing packages and workspace dependencies'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/package-management.mdc')
    assert '**Always use the workspace filter flag when adding packages to specific apps or packages.**' in text, "expected to find: " + '**Always use the workspace filter flag when adding packages to specific apps or packages.**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/package-management.mdc')
    assert 'When referencing internal packages, use the `workspace:*` protocol in package.json:' in text, "expected to find: " + 'When referencing internal packages, use the `workspace:*` protocol in package.json:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/shared-packages.mdc')
    assert '**Important**: Always import from `types`, not `app-types`. The API application has a local `types.ts` file that stores API-specific types which cannot be used by the Web application. Using `types` as' in text, "expected to find: " + '**Important**: Always import from `types`, not `app-types`. The API application has a local `types.ts` file that stores API-specific types which cannot be used by the Web application. Using `types` as'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/shared-packages.mdc')
    assert '**Important**: To prevent dependency cycle issues, import enums from the `types` package instead of `enums`. The `app-types` package re-exports all enums to break circular dependencies.' in text, "expected to find: " + '**Important**: To prevent dependency cycle issues, import enums from the `types` package instead of `enums`. The `app-types` package re-exports all enums to break circular dependencies.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/shared-packages.mdc')
    assert '**Important**: When creating a new database resource schema, always extend from `dbSchema` to include common database fields (`_id`, `createdOn`, `updatedOn`, etc.):' in text, "expected to find: " + '**Important**: When creating a new database resource schema, always extend from `dbSchema` to include common database fields (`_id`, `createdOn`, `updatedOn`, etc.):'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/validation-schemas.mdc')
    assert 'Validation-related constants in [packages/app-constants/src/validation.constants.ts](mdc:packages/app-constants/src/validation.constants.ts)' in text, "expected to find: " + 'Validation-related constants in [packages/app-constants/src/validation.constants.ts](mdc:packages/app-constants/src/validation.constants.ts)'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/validation-schemas.mdc')
    assert 'All validation schemas are centralized in the `schemas` package: [packages/schemas/src/](mdc:packages/schemas/src/)' in text, "expected to find: " + 'All validation schemas are centralized in the `schemas` package: [packages/schemas/src/](mdc:packages/schemas/src/)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('template/.cursor/rules/validation-schemas.mdc')
    assert 'Enums are centralized in [packages/enums/src/](mdc:packages/enums/src/). Use `z.nativeEnum()` for validation:' in text, "expected to find: " + 'Enums are centralized in [packages/enums/src/](mdc:packages/enums/src/). Use `z.nativeEnum()` for validation:'[:80]

