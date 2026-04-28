"""Behavioral checks for js-recall-feat-additional-improvements-to-cursorrules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/js-recall")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- **Note**: Alert thresholds and alerting rules should be configured in external monitoring systems (e.g., Datadog, PagerDuty) that consume these metrics - not implemented in application code' in text, "expected to find: " + '- **Note**: Alert thresholds and alerting rules should be configured in external monitoring systems (e.g., Datadog, PagerDuty) that consume these metrics - not implemented in application code'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- Prevent the linear query scaling problem: Instead of fetching a list then making separate queries per item, use joins or batch fetching' in text, "expected to find: " + '- Prevent the linear query scaling problem: Instead of fetching a list then making separate queries per item, use joins or batch fetching'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/api-specific-config.mdc')
    assert '- Always generate migrations using `pnpm db:gen-migrations` after schema changes which will automatically create the sql migration files' in text, "expected to find: " + '- Always generate migrations using `pnpm db:gen-migrations` after schema changes which will automatically create the sql migration files'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert '– **Inline Documentation:** Maintain excellent, thorough inline documentation (e.g., comments for functions, methods, types, classes, and complex logic).' in text, "expected to find: " + '– **Inline Documentation:** Maintain excellent, thorough inline documentation (e.g., comments for functions, methods, types, classes, and complex logic).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert '- **AI AGENT REQUIREMENT**: When implementing a new method that replaces an old one, you MUST remove the old implementation in the same changeset' in text, "expected to find: " + '- **AI AGENT REQUIREMENT**: When implementing a new method that replaces an old one, you MUST remove the old implementation in the same changeset'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-general-practices.mdc')
    assert '- **NEVER** use words like "new", "optimized", "efficient", "replaces", "improved", "better", "faster", "atomic" in comments or TSDoc' in text, "expected to find: " + '- **NEVER** use words like "new", "optimized", "efficient", "replaces", "improved", "better", "faster", "atomic" in comments or TSDoc'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert "- **Explicit Return Types:** All functions must have explicit return types. Never rely on TypeScript's type inference for function returns." in text, "expected to find: " + "- **Explicit Return Types:** All functions must have explicit return types. Never rely on TypeScript's type inference for function returns."[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert '- **Named Types over Ad-hoc Types:** Prefer creating named types/interfaces over inline type definitions, especially when:' in text, "expected to find: " + '- **Named Types over Ad-hoc Types:** Prefer creating named types/interfaces over inline type definitions, especially when:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/org-typescript-standards.mdc')
    assert '- Example: ✅ GOOD: `interface User { id: string; name: string; email: string }` then `function getUser(): User`' in text, "expected to find: " + '- Example: ✅ GOOD: `interface User { id: string; name: string; email: string }` then `function getUser(): User`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/repo-specific-config.mdc')
    assert '- Boolean flags instead of string enums when binary (e.g., `isLong` vs `side: "long" | "short"`)' in text, "expected to find: " + '- Boolean flags instead of string enums when binary (e.g., `isLong` vs `side: "long" | "short"`)'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/repo-specific-config.mdc')
    assert '- Optional fields: Use `| null` for API, handle in frontend' in text, "expected to find: " + '- Optional fields: Use `| null` for API, handle in frontend'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/repo-specific-config.mdc')
    assert '- Dates as ISO 8601 strings (e.g., `2024-01-01T00:00:00Z`)' in text, "expected to find: " + '- Dates as ISO 8601 strings (e.g., `2024-01-01T00:00:00Z`)'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Avoid situations where the number of database queries scales linearly (e.g. fetching a list then making separate queries per item). Use joins or batch fetching instead' in text, "expected to find: " + '- Avoid situations where the number of database queries scales linearly (e.g. fetching a list then making separate queries per item). Use joins or batch fetching instead'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Be Explicit About Context**: Claude works best when given clear context about the current task, existing patterns, and constraints.' in text, "expected to find: " + '1. **Be Explicit About Context**: Claude works best when given clear context about the current task, existing patterns, and constraints.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Leverage Existing Patterns**: Always point Claude to existing implementations of similar features in the codebase.' in text, "expected to find: " + '2. **Leverage Existing Patterns**: Always point Claude to existing implementations of similar features in the codebase.'[:80]

