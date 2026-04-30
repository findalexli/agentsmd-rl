"""Behavioral checks for vite-plus-fix-condense-vite-agentsmd-content (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vite-plus")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/AGENTS.md')
    assert 'This project is using Vite+, a unified toolchain built on top of Vite, Rolldown, Vitest, tsdown, Oxlint, Oxfmt, and Vite Task. Vite+ wraps runtime management, package management, and frontend tooling ' in text, "expected to find: " + 'This project is using Vite+, a unified toolchain built on top of Vite, Rolldown, Vitest, tsdown, Oxlint, Oxfmt, and Vite Task. Vite+ wraps runtime management, package management, and frontend tooling '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/AGENTS.md')
    assert "- **Import JavaScript modules from `vite-plus`:** Import modules from the `vite-plus` dependency, not from `vite` or `vitest`. For example, `import { defineConfig } from 'vite-plus';` or `import { exp" in text, "expected to find: " + "- **Import JavaScript modules from `vite-plus`:** Import modules from the `vite-plus` dependency, not from `vite` or `vitest`. For example, `import { defineConfig } from 'vite-plus';` or `import { exp"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/AGENTS.md')
    assert '- **Running scripts:** Vite+ built-in commands (`vp lint`, `vp dev`, `vp build`, `vp test`, etc.) always run the Vite+ built-in tool. Use `vp run <script>` to run `package.json` scripts or tasks defin' in text, "expected to find: " + '- **Running scripts:** Vite+ built-in commands (`vp lint`, `vp dev`, `vp build`, `vp test`, etc.) always run the Vite+ built-in tool. Use `vp run <script>` to run `package.json` scripts or tasks defin'[:80]

