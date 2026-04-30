"""Behavioral checks for supabase-fix-added-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/supabase")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/studio-useStaticEffectEvent.mdc')
    assert "The `useStaticEffectEvent` hook (located at `apps/studio/hooks/useStaticEffectEvent.ts`) is a userland implementation of React's `useEffectEvent` pattern. It solves the stale closure problem by provid" in text, "expected to find: " + "The `useStaticEffectEvent` hook (located at `apps/studio/hooks/useStaticEffectEvent.ts`) is a userland implementation of React's `useEffectEvent` pattern. It solves the stale closure problem by provid"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/studio-useStaticEffectEvent.mdc')
    assert "When using `useEffect`, you often need to access props or state inside your Effect, but you don't want changes to those values to re-run the Effect. Without `useStaticEffectEvent`, you'd face two bad " in text, "expected to find: " + "When using `useEffect`, you often need to access props or state inside your Effect, but you don't want changes to those values to re-run the Effect. Without `useStaticEffectEvent`, you'd face two bad "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/studio-useStaticEffectEvent.mdc')
    assert "This hook is a polyfill for React's experimental `useEffectEvent` (now stable in React 19.2). The core concept is identical:" in text, "expected to find: " + "This hook is a polyfill for React's experimental `useEffectEvent` (now stable in React 19.2). The core concept is identical:"[:80]

