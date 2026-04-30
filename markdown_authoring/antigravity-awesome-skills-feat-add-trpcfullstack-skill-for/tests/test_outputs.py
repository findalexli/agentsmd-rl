"""Behavioral checks for antigravity-awesome-skills-feat-add-trpcfullstack-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/trpc-fullstack/SKILL.md')
    assert 'tRPC lets you build fully type-safe APIs without writing a schema or code-generation step. Your TypeScript types flow from the server router directly to the client — so every API call is autocompleted' in text, "expected to find: " + 'tRPC lets you build fully type-safe APIs without writing a schema or code-generation step. Your TypeScript types flow from the server router directly to the client — so every API call is autocompleted'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/trpc-fullstack/SKILL.md')
    assert '`context` is shared state passed to every procedure — auth session, database client, request headers, etc. It is built once per request in a context factory. **Important:** Next.js App Router and Page' in text, "expected to find: " + '`context` is shared state passed to every procedure — auth session, database client, request headers, etc. It is built once per request in a context factory. **Important:** Next.js App Router and Page'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/trpc-fullstack/SKILL.md')
    assert '**Solution:** Ensure `createTRPCContext` uses the correct server-side auth call (e.g. `auth()` from Next-Auth v5) and is not receiving a Pages Router `req/res` cast via `as any` in an App Router handl' in text, "expected to find: " + '**Solution:** Ensure `createTRPCContext` uses the correct server-side auth call (e.g. `auth()` from Next-Auth v5) and is not receiving a Pages Router `req/res` cast via `as any` in an App Router handl'[:80]

