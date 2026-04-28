"""Behavioral checks for celestia-core-chore-init-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/celestia-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Celestia-core is a fork of CometBFT (formerly Tendermint) — a BFT consensus engine — with Celestia-specific modifications for data availability. The Go module path is `github.com/cometbft/cometbft`. I' in text, "expected to find: " + 'Celestia-core is a fork of CometBFT (formerly Tendermint) — a BFT consensus engine — with Celestia-specific modifications for data availability. The Go module path is `github.com/cometbft/cometbft`. I'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Protobuf:** Definitions live in `proto/tendermint/`. Generated code uses `gogofaster` plugin via buf. After `make proto-gen`, ABCI types are moved to `abci/types/` and gRPC types to `rpc/grpc/`.' in text, "expected to find: " + '**Protobuf:** Definitions live in `proto/tendermint/`. Generated code uses `gogofaster` plugin via buf. After `make proto-gen`, ABCI types are moved to `abci/types/` and gRPC types to `rpc/grpc/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Every PR needs a changelog entry at `.changelog/unreleased/{category}/{issue-or-pr-number}-{description}.md` where category is one of: `improvements`, `breaking-changes`, `bug-fixes`, `features`.' in text, "expected to find: " + 'Every PR needs a changelog entry at `.changelog/unreleased/{category}/{issue-or-pr-number}-{description}.md` where category is one of: `improvements`, `breaking-changes`, `bug-fixes`, `features`.'[:80]

