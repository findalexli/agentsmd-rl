"""Behavioral checks for formbricks-chore-consolidate-agent-instructions-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/formbricks")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/build-and-deployment.mdc')
    assert '.cursor/rules/build-and-deployment.mdc' in text, "expected to find: " + '.cursor/rules/build-and-deployment.mdc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/cache-optimization.mdc')
    assert '.cursor/rules/cache-optimization.mdc' in text, "expected to find: " + '.cursor/rules/cache-optimization.mdc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/database-performance.mdc')
    assert '.cursor/rules/database-performance.mdc' in text, "expected to find: " + '.cursor/rules/database-performance.mdc'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/database.mdc')
    assert '.cursor/rules/database.mdc' in text, "expected to find: " + '.cursor/rules/database.mdc'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/documentations.mdc')
    assert '.cursor/rules/documentations.mdc' in text, "expected to find: " + '.cursor/rules/documentations.mdc'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/formbricks-architecture.mdc')
    assert '.cursor/rules/formbricks-architecture.mdc' in text, "expected to find: " + '.cursor/rules/formbricks-architecture.mdc'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/github-actions-security.mdc')
    assert '.cursor/rules/github-actions-security.mdc' in text, "expected to find: " + '.cursor/rules/github-actions-security.mdc'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/i18n-management.mdc')
    assert '.cursor/rules/i18n-management.mdc' in text, "expected to find: " + '.cursor/rules/i18n-management.mdc'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/react-context-patterns.mdc')
    assert '.cursor/rules/react-context-patterns.mdc' in text, "expected to find: " + '.cursor/rules/react-context-patterns.mdc'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/review-and-refine.mdc')
    assert '.cursor/rules/review-and-refine.mdc' in text, "expected to find: " + '.cursor/rules/review-and-refine.mdc'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/storybook-component-migration.mdc')
    assert '.cursor/rules/storybook-component-migration.mdc' in text, "expected to find: " + '.cursor/rules/storybook-component-migration.mdc'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/storybook-create-new-story.mdc')
    assert '.cursor/rules/storybook-create-new-story.mdc' in text, "expected to find: " + '.cursor/rules/storybook-create-new-story.mdc'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Next.js app router lives in `apps/web/app` with route groups like `(app)` and `(auth)`. Services live in `apps/web/lib`, feature modules in `apps/web/modules`.' in text, "expected to find: " + '- Next.js app router lives in `apps/web/app` with route groups like `(app)` and `(auth)`. Services live in `apps/web/lib`, feature modules in `apps/web/modules`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Lingo.dev is automatically translating strings from en-US into other languages on commit. Run `pnpm i18n` to generate missing translations and validate keys.' in text, "expected to find: " + '- Lingo.dev is automatically translating strings from en-US into other languages on commit. Run `pnpm i18n` to generate missing translations and validate keys.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Context providers should guard against missing provider usage and use cleanup patterns that snapshot refs inside `useEffect` to avoid React hooks warnings' in text, "expected to find: " + '- Context providers should guard against missing provider usage and use cleanup patterns that snapshot refs inside `useEffect` to avoid React hooks warnings'[:80]

