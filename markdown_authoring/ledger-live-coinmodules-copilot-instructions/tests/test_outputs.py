"""Behavioral checks for ledger-live-coinmodules-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Prefer native dependencies from the blockchain foundation/ecosystem and well-established open-source libraries. Avoid proprietary **third-party** SDKs or closed-source vendor packages (e.g. coin-vendo' in text, "expected to find: " + 'Prefer native dependencies from the blockchain foundation/ecosystem and well-established open-source libraries. Avoid proprietary **third-party** SDKs or closed-source vendor packages (e.g. coin-vendo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Alpaca path** (preferred)— The coin module exports `createApi(config, currencyId)` implementing `AlpacaApi`. Families listed in the `alpacaized` map in `libs/ledger-live-common/src/bridge/impl.ts' in text, "expected to find: " + '1. **Alpaca path** (preferred)— The coin module exports `createApi(config, currencyId)` implementing `AlpacaApi`. Families listed in the `alpacaized` map in `libs/ledger-live-common/src/bridge/impl.ts'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. **Classic JS Bridge** (legacy, should not be used) — The coin module exports `createBridges(signerContext, coinConfig)` returning `{ currencyBridge, accountBridge }`. This is wired via `libs/ledger' in text, "expected to find: " + '2. **Classic JS Bridge** (legacy, should not be used) — The coin module exports `createBridges(signerContext, coinConfig)` returning `{ currencyBridge, accountBridge }`. This is wired via `libs/ledger'[:80]

