"""Behavioral checks for hyperlane-warp-ui-template-docs-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperlane-warp-ui-template")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Hyperlane Warp UI Template is a Next.js web application for cross-chain token transfers using [Hyperlane Warp Routes](https://docs.hyperlane.xyz/docs/reference/applications/warp-routes). It enables pe' in text, "expected to find: " + 'Hyperlane Warp UI Template is a Next.js web application for cross-chain token transfers using [Hyperlane Warp Routes](https://docs.hyperlane.xyz/docs/reference/applications/warp-routes). It enables pe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Tests use Vitest and are co-located with source files using the `*.test.ts` naming convention. Vitest automatically discovers and runs all matching test files.' in text, "expected to find: " + 'Tests use Vitest and are co-located with source files using the `*.test.ts` naming convention. Vitest automatically discovers and runs all matching test files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Wallets**: Each blockchain uses distinct, composable wallet providers (EVM/RainbowKit, Solana, Cosmos, Starknet, Radix)' in text, "expected to find: " + '- **Wallets**: Each blockchain uses distinct, composable wallet providers (EVM/RainbowKit, Solana, Cosmos, Starknet, Radix)'[:80]

