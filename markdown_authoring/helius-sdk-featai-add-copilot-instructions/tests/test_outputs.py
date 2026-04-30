"""Behavioral checks for helius-sdk-featai-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/helius-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'TypeScript SDK for Helius APIs and Solana development. Built on `@solana/kit` with dual ESM/CJS output, lazy loading, and tree-shaking. For full contributor details see [CLAUDE.md](../CLAUDE.md).' in text, "expected to find: " + 'TypeScript SDK for Helius APIs and Solana development. Built on `@solana/kit` with dual ESM/CJS output, lazy loading, and tree-shaking. For full contributor details see [CLAUDE.md](../CLAUDE.md).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Every method and sub-client must use `defineLazyMethod` or `defineLazyNamespace` from `src/rpc/lazy.ts`. This is mandatory — never eagerly import method modules from `src/rpc/index.ts`.' in text, "expected to find: " + 'Every method and sub-client must use `defineLazyMethod` or `defineLazyNamespace` from `src/rpc/lazy.ts`. This is mandatory — never eagerly import method modules from `src/rpc/index.ts`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This SDK uses `@solana/kit` exclusively. Never import from `@solana/web3.js`. When writing Solana types, helpers, or transaction logic, always reach for `@solana/kit` equivalents.' in text, "expected to find: " + 'This SDK uses `@solana/kit` exclusively. Never import from `@solana/web3.js`. When writing Solana types, helpers, or transaction logic, always reach for `@solana/kit` equivalents.'[:80]

