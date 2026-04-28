"""Behavioral checks for lobehub-docs-make-agents-the-source (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobehub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **Register the desktop route tree in both configs:** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` must stay in sync (same paths and nesting). Upda' in text, "expected to find: " + '4. **Register the desktop route tree in both configs:** `src/spa/router/desktopRouter.config.tsx` and `src/spa/router/desktopRouter.config.desktop.tsx` must stay in sync (same paths and nesting). Upda'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`src/spa/`** – SPA entry points (`entry.web.tsx`, `entry.mobile.tsx`, `entry.desktop.tsx`, `entry.popup.tsx`) and React Router config (`router/`, with `desktopRouter.config.*`, `mobileRouter.confi' in text, "expected to find: " + '- **`src/spa/`** – SPA entry points (`entry.web.tsx`, `entry.mobile.tsx`, `entry.desktop.tsx`, `entry.popup.tsx`) and React Router config (`router/`, with `desktopRouter.config.*`, `mobileRouter.confi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `@lobehub/ui`, antd for components; antd-style for CSS-in-JS — **prefer `createStaticStyles` with `cssVar.*`** (zero-runtime); only fall back to `createStyles` + `token` when styles genuinely need r' in text, "expected to find: " + '- `@lobehub/ui`, antd for components; antd-style for CSS-in-JS — **prefer `createStaticStyles` with `cssVar.*`** (zero-runtime); only fall back to `createStyles` + `token` when styles genuinely need r'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

