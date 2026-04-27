"""Behavioral checks for astro-add-agent-skill-vite-dep (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/astro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/optimize-deps/SKILL.md')
    assert "description: Deep reference on Vite's dep optimizer (optimizeDeps) as it applies to the Astro monorepo. Covers how the optimizer works, how non-JS files are handled during dep scanning, the roles of v" in text, "expected to find: " + "description: Deep reference on Vite's dep optimizer (optimizeDeps) as it applies to the Astro monorepo. Covers how the optimizer works, how non-JS files are handled during dep scanning, the roles of v"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/optimize-deps/SKILL.md')
    assert "`astro build` uses Rollup and handles CJS→ESM transformation reliably. `astro dev` uses Vite 7's dev server, which serves modules individually and relies on esbuild's **dep optimizer** to pre-bundle c" in text, "expected to find: " + "`astro build` uses Rollup and handles CJS→ESM transformation reliably. `astro dev` uses Vite 7's dev server, which serves modules individually and relies on esbuild's **dep optimizer** to pre-bundle c"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/optimize-deps/SKILL.md')
    assert '**Important subtlety:** `shouldExternalizeDep` in Vite returns `true` when `resolved === rawId` (i.e. the file was passed as an absolute path entry). This means absolute-path entries that match `htmlT' in text, "expected to find: " + '**Important subtlety:** `shouldExternalizeDep` in Vite returns `true` when `resolved === rawId` (i.e. the file was passed as an absolute path entry). This means absolute-path entries that match `htmlT'[:80]

