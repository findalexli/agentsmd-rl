"""Behavioral checks for remix-add-shipped-app-skills-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/remix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/add-sqlite-database/SKILL.md')
    assert '- [ ] `lib/db.ts` creates `db` using `createSqliteDatabaseAdapter(...)` and `createDatabase(...)`' in text, "expected to find: " + '- [ ] `lib/db.ts` creates `db` using `createSqliteDatabaseAdapter(...)` and `createDatabase(...)`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/add-sqlite-database/SKILL.md')
    assert '- [ ] `app/root/controller.tsx` imports and uses `db` in the root `Controller` object' in text, "expected to find: " + '- [ ] `app/root/controller.tsx` imports and uses `db` in the root `Controller` object'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/add-sqlite-database/SKILL.md')
    assert '4. Use `db` in the root controller (same controller style as the scaffolding skill).' in text, "expected to find: " + '4. Use `db` in the root controller (same controller style as the scaffolding skill).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/new-route/SKILL.md')
    assert 'description: Add a new route to a Remix app by defining it in app/routes.ts, implementing the handler, wiring it in app/router.ts, and using route href helpers for links and forms.' in text, "expected to find: " + 'description: Add a new route to a Remix app by defining it in app/routes.ts, implementing the handler, wiring it in app/router.ts, and using route href helpers for links and forms.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/new-route/SKILL.md')
    assert '- Add or update `app/router.test.ts` (or a route-specific `*.test.ts`) to verify method + path + response behavior.' in text, "expected to find: " + '- Add or update `app/router.test.ts` (or a route-specific `*.test.ts`) to verify method + path + response behavior.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/new-route/SKILL.md')
    assert '- Use method helpers when a route should match only one method (`get`, `post`, `put`, `del`, `form`).' in text, "expected to find: " + '- Use method helpers when a route should match only one method (`get`, `post`, `put`, `del`, `form`).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/scaffold-remix-app/SKILL.md')
    assert 'description: Use when you are in a newly created project directory and want to scaffold the initial structure for a Remix app you can build features on top of.' in text, "expected to find: " + 'description: Use when you are in a newly created project directory and want to scaffold the initial structure for a Remix app you can build features on top of.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/scaffold-remix-app/SKILL.md')
    assert 'Components in `remix/component` are not React components. They follow the Remix component model, where a component function returns a render function.' in text, "expected to find: " + 'Components in `remix/component` are not React components. They follow the Remix component model, where a component function returns a render function.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('app-skills/scaffold-remix-app/SKILL.md')
    assert 'Use this skill when you are in a newly created directory and need to scaffold a basic Remix app that runs on Node.js.' in text, "expected to find: " + 'Use this skill when you are in a newly created directory and need to scaffold a basic Remix app that runs on Node.js.'[:80]

