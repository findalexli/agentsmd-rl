"""Behavioral checks for tycho-indexer-chore-improve-and-split-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tycho-indexer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- For `rstest` parameterized tests, **name each case** with `#[case::descriptive_name(...)]` — test names should be self-documenting so failures are immediately identifiable' in text, "expected to find: " + '- For `rstest` parameterized tests, **name each case** with `#[case::descriptive_name(...)]` — test names should be self-documenting so failures are immediately identifiable'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Tycho is a multi-crate Rust workspace for indexing DEX/DeFi protocol data from blockchains, streaming real-time state to solvers via WebSocket deltas and HTTP snapshots.' in text, "expected to find: " + 'Tycho is a multi-crate Rust workspace for indexing DEX/DeFi protocol data from blockchains, streaming real-time state to solvers via WebSocket deltas and HTTP snapshots.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **tycho-ethereum**: Ethereum specific implementations: RPC, token analysis, EVM account/trace extraction' in text, "expected to find: " + '- **tycho-ethereum**: Ethereum specific implementations: RPC, token analysis, EVM account/trace extraction'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-client/CLAUDE.md')
    assert '4. Synchronizers classified as `Started | Ready | Delayed | Stale | Advanced | Ended`; stale ones are kept but skipped' in text, "expected to find: " + '4. Synchronizers classified as `Started | Ready | Delayed | Stale | Advanced | Ended`; stale ones are kept but skipped'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-client/CLAUDE.md')
    assert 'synchronizer.rs   ProtocolStateSynchronizer — manages snapshot + delta sync for one extractor' in text, "expected to find: " + 'synchronizer.rs   ProtocolStateSynchronizer — manages snapshot + delta sync for one extractor'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-client/CLAUDE.md')
    assert 'Consumer library implementing the snapshot + deltas pattern for real-time protocol state.' in text, "expected to find: " + 'Consumer library implementing the snapshot + deltas pattern for real-time protocol state.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-common/CLAUDE.md')
    assert '- **`protocol_sim`** — `ProtocolSim` core trait (quote, price, state transition); implemented by protocol-specific simulators; To be replaced by SwapQuoter trait in the future.' in text, "expected to find: " + '- **`protocol_sim`** — `ProtocolSim` core trait (quote, price, state transition); implemented by protocol-specific simulators; To be replaced by SwapQuoter trait in the future.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-common/CLAUDE.md')
    assert '- **`dto`** — JSON-serialisable mirrors of `models/` types for HTTP/WebSocket responses; used by tycho-indexer (server) and tycho-client (consumer)' in text, "expected to find: " + '- **`dto`** — JSON-serialisable mirrors of `models/` types for HTTP/WebSocket responses; used by tycho-indexer (server) and tycho-client (consumer)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-common/CLAUDE.md')
    assert '- **`storage`** — Async gateway traits (`ProtocolGateway`, `ContractStateGateway`, …) that tycho-storage implements over Diesel/Postgres' in text, "expected to find: " + '- **`storage`** — Async gateway traits (`ProtocolGateway`, `ContractStateGateway`, …) that tycho-storage implements over Diesel/Postgres'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-ethereum/CLAUDE.md')
    assert "All services depend on `rpc/` for RPC calls and on `erc20.rs` for ABI encoding. The entrypoint tracer's slot detectors feed into `account_extractor` when slot layout is unknown." in text, "expected to find: " + "All services depend on `rpc/` for RPC calls and on `erc20.rs` for ABI encoding. The entrypoint tracer's slot detectors feed into `account_extractor` when slot layout is unknown."[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-ethereum/CLAUDE.md')
    assert 'Ethereum-specific implementations of traits defined in `tycho-common`. Consumed exclusively by `tycho-indexer`.' in text, "expected to find: " + 'Ethereum-specific implementations of traits defined in `tycho-common`. Consumed exclusively by `tycho-indexer`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-ethereum/CLAUDE.md')
    assert '├─ token_analyzer.rs        Simulates token transfers via trace_callMany; classifies token quality' in text, "expected to find: " + '├─ token_analyzer.rs        Simulates token transfers via trace_callMany; classifies token quality'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-indexer/CLAUDE.md')
    assert 'runner.rs                 ExtractorRunner: drives the Substreams stream; ExtractorHandle for control' in text, "expected to find: " + 'runner.rs                 ExtractorRunner: drives the Substreams stream; ExtractorHandle for control'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-indexer/CLAUDE.md')
    assert '6. When `ReorgBuffer` has `>= commit_batch_size` blocks before `finalized_block_height`, drain them' in text, "expected to find: " + '6. When `ReorgBuffer` has `>= commit_batch_size` blocks before `finalized_block_height`, drain them'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-indexer/CLAUDE.md')
    assert 'Main indexing engine: connects to Substreams, processes block data, persists finalized state, and' in text, "expected to find: " + 'Main indexing engine: connects to Substreams, processes block data, persists finalized state, and'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-storage/CLAUDE.md')
    assert '`chain`, `contract`, `protocol`, `entry_point`, and `extraction_state`—each adding methods to' in text, "expected to find: " + '`chain`, `contract`, `protocol`, `entry_point`, and `extraction_state`—each adding methods to'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-storage/CLAUDE.md')
    assert 'Both delegate every actual SQL call to `PostgresGateway` (unexported). Domain logic lives in' in text, "expected to find: " + 'Both delegate every actual SQL call to `PostgresGateway` (unexported). Domain logic lives in'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('tycho-storage/CLAUDE.md')
    assert '`versioning` is the only module without a DB table of its own; it provides the shared traits' in text, "expected to find: " + '`versioning` is the only module without a DB table of its own; it provides the shared traits'[:80]

