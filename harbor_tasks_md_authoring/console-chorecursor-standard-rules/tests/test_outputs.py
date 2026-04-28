"""Behavioral checks for console-chorecursor-standard-rules (markdown_authoring task).

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
    text = _read('.cursor/rules/development-commands.mdc')
    assert 'npx nx run-many --all --target=lint --parallel  # Lint all projects' in text, "expected to find: " + 'npx nx run-many --all --target=lint --parallel  # Lint all projects'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-commands.mdc')
    assert '- IDE configurations for ESLint and Prettier are included' in text, "expected to find: " + '- IDE configurations for ESLint and Prettier are included'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/development-commands.mdc')
    assert 'description: Common development commands and workflows' in text, "expected to find: " + 'description: Common development commands and workflows'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert '- **Types/Interfaces**: PascalCase with `Props` suffix for interfaces if needed' in text, "expected to find: " + '- **Types/Interfaces**: PascalCase with `Props` suffix for interfaces if needed'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert 'description: Naming conventions for files, components, and variables' in text, "expected to find: " + 'description: Naming conventions for files, components, and variables'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/naming-conventions.mdc')
    assert '- **Private members**: prefix with underscore `_privateMember`' in text, "expected to find: " + '- **Private members**: prefix with underscore `_privateMember`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pre-commit-workflow.mdc')
    assert 'This project uses **semantic-release** with conventional commit format:' in text, "expected to find: " + 'This project uses **semantic-release** with conventional commit format:'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pre-commit-workflow.mdc')
    assert 'description: Pre-commit verification workflow and quality checks' in text, "expected to find: " + 'description: Pre-commit verification workflow and quality checks'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pre-commit-workflow.mdc')
    assert 'echo "❌ Format check failed. Run \'npx nx format:write\' to fix."' in text, "expected to find: " + 'echo "❌ Format check failed. Run \'npx nx format:write\' to fix."'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-architecture.mdc')
    assert 'description: Qovery Console project architecture and structure guidelines' in text, "expected to find: " + 'description: Qovery Console project architecture and structure guidelines'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-architecture.mdc')
    assert '- Use Nx generators to create new components/libs' in text, "expected to find: " + '- Use Nx generators to create new components/libs'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/project-architecture.mdc')
    assert '├── domains/         # Business logic by domain' in text, "expected to find: " + '├── domains/         # Business logic by domain'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-typescript-standards.mdc')
    assert "- ALWAYS use inline type imports: `import { type MyType, myFunction } from './module'`" in text, "expected to find: " + "- ALWAYS use inline type imports: `import { type MyType, myFunction } from './module'`"[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-typescript-standards.mdc')
    assert '- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes' in text, "expected to find: " + '- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-typescript-standards.mdc')
    assert 'description: React and TypeScript coding standards for Qovery Console' in text, "expected to find: " + 'description: React and TypeScript coding standards for Qovery Console'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-standards.mdc')
    assert '- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes' in text, "expected to find: " + '- Use `clsx` or `twMerge` from `@qovery/shared/util-js` for conditional classes'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-standards.mdc')
    assert '- TailwindCSS only (no CSS modules or styled-components in new code)' in text, "expected to find: " + '- TailwindCSS only (no CSS modules or styled-components in new code)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-standards.mdc')
    assert 'description: Styling and design standards using TailwindCSS' in text, "expected to find: " + 'description: Styling and design standards using TailwindCSS'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing-standards.mdc')
    assert "globs: ['**/*.spec.ts', '**/*.spec.tsx', '**/*.test.ts', '**/*.test.tsx']" in text, "expected to find: " + "globs: ['**/*.spec.ts', '**/*.spec.tsx', '**/*.test.ts', '**/*.test.tsx']"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing-standards.mdc')
    assert 'description: Testing standards and practices for Qovery Console' in text, "expected to find: " + 'description: Testing standards and practices for Qovery Console'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing-standards.mdc')
    assert '- Use `renderWithProviders` from `@qovery/shared/util-tests`' in text, "expected to find: " + '- Use `renderWithProviders` from `@qovery/shared/util-tests`'[:80]

