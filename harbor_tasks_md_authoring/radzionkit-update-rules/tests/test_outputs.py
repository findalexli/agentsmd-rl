"""Behavioral checks for radzionkit-update-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/radzionkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/add-library.mdc')
    assert '.cursor/rules/add-library.mdc' in text, "expected to find: " + '.cursor/rules/add-library.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/assert.mdc')
    assert 'description: Use shouldBePresent() instead of optional chaining or default values for required values' in text, "expected to find: " + 'description: Use shouldBePresent() instead of optional chaining or default values for required values'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/assert.mdc')
    assert '- Avoid optional chaining and default values for required data' in text, "expected to find: " + '- Avoid optional chaining and default values for required data'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/assert.mdc')
    assert '- Use `shouldBePresent()` for values that should always exist' in text, "expected to find: " + '- Use `shouldBePresent()` for values that should always exist'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/attempt-over-try-catch.mdc')
    assert 'description: USE attempt utility WHEN handling errors is necessary FOR user feedback or alternative logic, NOT for logging' in text, "expected to find: " + 'description: USE attempt utility WHEN handling errors is necessary FOR user feedback or alternative logic, NOT for logging'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/attempt-over-try-catch.mdc')
    assert "const data = 'data' in primaryResult ? primaryResult.data : await fetchBackup()" in text, "expected to find: " + "const data = 'data' in primaryResult ? primaryResult.data : await fetchBackup()"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/attempt-over-try-catch.mdc')
    assert "- **Let errors bubble up naturally** - don't wrap functions just to log errors" in text, "expected to find: " + "- **Let errors bubble up naturally** - don't wrap functions just to log errors"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cusor-rules.mdc')
    assert '.cursor/rules/cusor-rules.mdc' in text, "expected to find: " + '.cursor/rules/cusor-rules.mdc'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/default-rule-scoping.mdc')
    assert 'When creating Cursor rules for this TypeScript codebase, default to using file-specific targeting rather than descriptions or always-apply rules.' in text, "expected to find: " + 'When creating Cursor rules for this TypeScript codebase, default to using file-specific targeting rather than descriptions or always-apply rules.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/default-rule-scoping.mdc')
    assert 'File-specific targeting ensures rules are contextually relevant and reduces noise for the AI agent when working on specific file types.' in text, "expected to find: " + 'File-specific targeting ensures rules are contextually relevant and reduces noise for the AI agent when working on specific file types.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/default-rule-scoping.mdc')
    assert '- Use `alwaysApply: true` only for project-wide architectural guidance' in text, "expected to find: " + '- Use `alwaysApply: true` only for project-wide architectural guidance'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/eslint-autofix.mdc')
    assert 'description: Use ESLint autofix (yarn) only for issues that ESLint can automatically fix, like import sorting; never sort imports manually.' in text, "expected to find: " + 'description: Use ESLint autofix (yarn) only for issues that ESLint can automatically fix, like import sorting; never sort imports manually.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/eslint-autofix.mdc')
    assert '- **Use ESLint auto-fix only for issues that ESLint can automatically resolve**, such as import sorting. Do not sort imports manually.' in text, "expected to find: " + '- **Use ESLint auto-fix only for issues that ESLint can automatically resolve**, such as import sorting. Do not sort imports manually.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/eslint-autofix.mdc')
    assert '- For issues that require manual fixes, address them directly in the code rather than relying on autofix.' in text, "expected to find: " + '- For issues that require manual fixes, address them directly in the code rather than relying on autofix.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/functions.mdc')
    assert "1. **Two obvious arguments**: When the function has exactly two parameters that are very clear from context and it's unlikely a third parameter will be added" in text, "expected to find: " + "1. **Two obvious arguments**: When the function has exactly two parameters that are very clear from context and it's unlikely a third parameter will be added"[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/functions.mdc')
    assert '3. **Well-established patterns**: Functions following established API patterns (like DOM APIs, standard library functions)' in text, "expected to find: " + '3. **Well-established patterns**: Functions following established API patterns (like DOM APIs, standard library functions)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/functions.mdc')
    assert '2. **Required + optional props**: When the first argument is required and the second is optional configuration/props' in text, "expected to find: " + '2. **Required + optional props**: When the first argument is required and the second is optional configuration/props'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/imports.mdc')
    assert 'description: Import path guidelines for monorepo packages - use relative paths within packages, absolute paths for cross-package imports' in text, "expected to find: " + 'description: Import path guidelines for monorepo packages - use relative paths within packages, absolute paths for cross-package imports'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/imports.mdc')
    assert "- Do not use relative path imports like '../../../../state/isInitiatingDevice' for cross-package imports" in text, "expected to find: " + "- Do not use relative path imports like '../../../../state/isInitiatingDevice' for cross-package imports"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/imports.mdc')
    assert '- Always use absolute package paths (not relative paths) when importing from a different package' in text, "expected to find: " + '- Always use absolute package paths (not relative paths) when importing from a different package'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/package-manager.mdc')
    assert 'globs: *.ts,*.tsx' in text, "expected to find: " + 'globs: *.ts,*.tsx'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/readable-code-over-comments.mdc')
    assert 'description: Prefer writing self-documenting, readable code over adding explanatory comments. Add comments only when absolutely necessary for complex business logic or non-obvious decisions.' in text, "expected to find: " + 'description: Prefer writing self-documenting, readable code over adding explanatory comments. Add comments only when absolutely necessary for complex business logic or non-obvious decisions.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/readable-code-over-comments.mdc')
    assert 'Write self-documenting, readable code instead of adding explanatory comments. Add comments only when absolutely necessary.' in text, "expected to find: " + 'Write self-documenting, readable code instead of adding explanatory comments. Add comments only when absolutely necessary.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/readable-code-over-comments.mdc')
    assert '// Use base64 encoding for data transmission to ensure compatibility with legacy systems' in text, "expected to find: " + '// Use base64 encoding for data transmission to ensure compatibility with legacy systems'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resolver-pattern.mdc')
    assert 'description: Resolver pattern – how to design, name, type, and route resolvers (index.ts/resolver.ts/resolvers/*) with discriminants. Aligns with assert, pattern-matching, functions, attempt-over-try-' in text, "expected to find: " + 'description: Resolver pattern – how to design, name, type, and route resolvers (index.ts/resolver.ts/resolvers/*) with discriminants. Aligns with assert, pattern-matching, functions, attempt-over-try-'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resolver-pattern.mdc')
    assert '- Resolver function names include the full operation name and routing value for clarity, e.g., `getDevelopmentConfig`, `processWebRequest`, `deployAwsService`.' in text, "expected to find: " + '- Resolver function names include the full operation name and routing value for clarity, e.g., `getDevelopmentConfig`, `processWebRequest`, `deployAwsService`.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/resolver-pattern.mdc')
    assert '- Error handling: Use error handling utilities only when you must show errors to users or pursue alternative logic (attempt-over-try-catch rule).' in text, "expected to find: " + '- Error handling: Use error handling utilities only when you must show errors to users or pursue alternative logic (attempt-over-try-catch rule).'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trust-types-no-fallbacks.mdc')
    assert 'description: Trust TS-defined values – avoid optional chaining and fallbacks when types guarantee presence' in text, "expected to find: " + 'description: Trust TS-defined values – avoid optional chaining and fallbacks when types guarantee presence'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trust-types-no-fallbacks.mdc')
    assert "When a value's type is non-optional, use it directly. Do not add optional chaining or fallback values." in text, "expected to find: " + "When a value's type is non-optional, use it directly. Do not add optional chaining or fallback values."[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/trust-types-no-fallbacks.mdc')
    assert '- If a value may be missing, validate earlier and fail fast (e.g., assertions in @rules).' in text, "expected to find: " + '- If a value may be missing, validate earlier and fail fast (e.g., assertions in @rules).'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typecheck-guidance.mdc')
    assert "Type checking takes time, so it should only be used when there's a reasonable likelihood that changes could introduce type errors in other parts of the codebase. For isolated changes, the time investm" in text, "expected to find: " + "Type checking takes time, so it should only be used when there's a reasonable likelihood that changes could introduce type errors in other parts of the codebase. For isolated changes, the time investm"[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typecheck-guidance.mdc')
    assert 'Only run `yarn typecheck` from the root of the codebase when making changes that are **likely to affect other parts of the codebase**.' in text, "expected to find: " + 'Only run `yarn typecheck` from the root of the codebase when making changes that are **likely to affect other parts of the codebase**.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/typecheck-guidance.mdc')
    assert '- Modifying function signatures or return types that are used elsewhere' in text, "expected to find: " + '- Modifying function signatures or return types that are used elsewhere'[:80]

