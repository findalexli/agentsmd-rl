"""Behavioral checks for rspress-choreinfra-creation-of-agentsmd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rspress")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- `packages/core` (`@rspress/core`): CLI `rspress build/dev` (add `--watch`), config via `rspress.config.ts` using `defineConfig`; programmatic `import { defineConfig, loadConfig } from '@rspress/core" in text, "expected to find: " + "- `packages/core` (`@rspress/core`): CLI `rspress build/dev` (add `--watch`), config via `rspress.config.ts` using `defineConfig`; programmatic `import { defineConfig, loadConfig } from '@rspress/core"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Packages: `packages/core` (CLI + `@rspress/core`), `packages/theme-default` (Default theme), `packages/plugin-*` (Official plugins), `packages/create-rspress` (scaffolder).' in text, "expected to find: " + '- Packages: `packages/core` (CLI + `@rspress/core`), `packages/theme-default` (Default theme), `packages/plugin-*` (Official plugins), `packages/create-rspress` (scaffolder).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `packages/plugin-*` (`@rspress/plugin-*`): Official plugins like `plugin-algolia` (search), `plugin-llms` (LLM optimization), `plugin-typedoc` (API docs), etc.' in text, "expected to find: " + '- `packages/plugin-*` (`@rspress/plugin-*`): Official plugins like `plugin-algolia` (search), `plugin-llms` (LLM optimization), `plugin-typedoc` (API docs), etc.'[:80]

