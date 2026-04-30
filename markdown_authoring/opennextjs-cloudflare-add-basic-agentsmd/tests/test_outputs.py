"""Behavioral checks for opennextjs-cloudflare-add-basic-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opennextjs-cloudflare")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`@opennextjs/cloudflare` is an adapter that takes a Next.js `standalone` build and runs it on Cloudflare Workers via the Node.js compatibility layer. It sits on top of `@opennextjs/aws`, which provide' in text, "expected to find: " + '`@opennextjs/cloudflare` is an adapter that takes a Next.js `standalone` build and runs it on Cloudflare Workers via the Node.js compatibility layer. It sits on top of `@opennextjs/aws`, which provide'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **`src/cli/build/patches/`** contains esbuild plugins and `@ast-grep/napi` transforms that rewrite Next's emitted code to run on Workers. Every patch needs a spec, and ideally a minimal fixture of t" in text, "expected to find: " + "- **`src/cli/build/patches/`** contains esbuild plugins and `@ast-grep/napi` transforms that rewrite Next's emitted code to run on Workers. Every patch needs a spec, and ideally a minimal fixture of t"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Two things to keep separate in your head: **`src/api`** is the tiny surface users import at runtime; **`src/cli`** is the much larger build tool. Changes to `src/api` are user-visible; changes in `src' in text, "expected to find: " + 'Two things to keep separate in your head: **`src/api`** is the tiny surface users import at runtime; **`src/cli`** is the much larger build tool. Changes to `src/api` are user-visible; changes in `src'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

