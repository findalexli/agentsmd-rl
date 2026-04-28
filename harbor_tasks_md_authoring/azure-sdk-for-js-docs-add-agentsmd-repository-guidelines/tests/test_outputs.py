"""Behavioral checks for azure-sdk-for-js-docs-add-agentsmd-repository-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azure-sdk-for-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- ESLint via `@azure/eslint-plugin-azure-sdk` (do not disable rules). If the plugin isn’t built: `pnpm build --filter @azure/eslint-plugin-azure-sdk...`.' in text, "expected to find: " + '- ESLint via `@azure/eslint-plugin-azure-sdk` (do not disable rules). If the plugin isn’t built: `pnpm build --filter @azure/eslint-plugin-azure-sdk...`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Incremental builds: `pnpm turbo build -F {package name} --token 1` (build changed packages only; enables remote cache read).' in text, "expected to find: " + '- Incremental builds: `pnpm turbo build -F {package name} --token 1` (build changed packages only; enables remote cache read).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Filter examples: `pnpm test --filter @azure/web-pubsub`, `pnpm turbo build --filter sdk/web-pubsub/web-pubsub...`.' in text, "expected to find: " + '- Filter examples: `pnpm test --filter @azure/web-pubsub`, `pnpm turbo build --filter sdk/web-pubsub/web-pubsub...`.'[:80]

