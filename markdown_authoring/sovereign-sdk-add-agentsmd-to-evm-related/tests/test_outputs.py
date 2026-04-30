"""Behavioral checks for sovereign-sdk-add-agentsmd-to-evm-related (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sovereign-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/full-node/sov-ethereum/AGENTS.md')
    assert '| Block-id and pending assumption mismatch | `#2379`, `#2391` | Wrapper assumes L1 selector semantics not matching module semantics | Submission/local flows calling `sov-evm` use `BlockId` intentional' in text, "expected to find: " + '| Block-id and pending assumption mismatch | `#2379`, `#2391` | Wrapper assumes L1 selector semantics not matching module semantics | Submission/local flows calling `sov-evm` use `BlockId` intentional'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/full-node/sov-ethereum/AGENTS.md')
    assert '| Nonce/receipt flow surprises | `#2395`, `#2458` | Submission paths do not align with pending semantics | Wallet lifecycle (`send -> lookup tx -> receipt`) is coherent in pending and sealed states |' in text, "expected to find: " + '| Nonce/receipt flow surprises | `#2395`, `#2458` | Submission paths do not align with pending semantics | Wallet lifecycle (`send -> lookup tx -> receipt`) is coherent in pending and sealed states |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/full-node/sov-ethereum/AGENTS.md')
    assert '- Do not own here: canonical EVM state query logic (`eth_getBalance`, `eth_call`, `eth_estimateGas`, receipts, block assembly). Those belong in `crates/module-system/module-implementations/sov-evm`.' in text, "expected to find: " + '- Do not own here: canonical EVM state query logic (`eth_getBalance`, `eth_call`, `eth_estimateGas`, receipts, block assembly). Those belong in `crates/module-system/module-implementations/sov-evm`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/module-system/module-implementations/sov-evm/AGENTS.md')
    assert '`sov-evm` is the source of truth for EVM execution state and EVM JSON-RPC state queries. Most production RPC correctness bugs originate here, especially around block/tag resolution, fee context, and c' in text, "expected to find: " + '`sov-evm` is the source of truth for EVM execution state and EVM JSON-RPC state queries. Most production RPC correctness bugs originate here, especially around block/tag resolution, fee context, and c'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/module-system/module-implementations/sov-evm/AGENTS.md')
    assert '| Estimation/call behavior mismatch | `#2459` | Revert and gas estimation paths do not mirror real execution constraints | `eth_estimateGas` errors on revert with revert payload; no success value on r' in text, "expected to find: " + '| Estimation/call behavior mismatch | `#2459` | Revert and gas estimation paths do not mirror real execution constraints | `eth_estimateGas` errors on revert with revert payload; no success value on r'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('crates/module-system/module-implementations/sov-evm/AGENTS.md')
    assert '| Nonce/receipt lifecycle mismatch | `#2395`, `#2458` | Pending/soft-confirmed state not reflected consistently | Nonce, tx lookup, and receipt lookup agree during pending-to-sealed transitions |' in text, "expected to find: " + '| Nonce/receipt lifecycle mismatch | `#2395`, `#2458` | Pending/soft-confirmed state not reflected consistently | Nonce, tx lookup, and receipt lookup agree during pending-to-sealed transitions |'[:80]

