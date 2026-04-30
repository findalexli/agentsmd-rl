"""Behavioral checks for flow-go-sdk-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flow-go-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Regenerate mocks after interface changes**: run `make generate` whenever you touch `access.Client`, `access/grpc.RPCClient`, `access/grpc.ExecutionDataRPCClient`, or `access/http.handler` — `go:ge' in text, "expected to find: " + '- **Regenerate mocks after interface changes**: run `make generate` whenever you touch `access.Client`, `access/grpc.RPCClient`, `access/grpc.ExecutionDataRPCClient`, or `access/http.handler` — `go:ge'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **CGO is required by default** for BLS support (via `github.com/onflow/crypto`). Build with `CGO_ENABLED=1`. You can build with `CGO_ENABLED=0` but must also pass the `no-cgo` build tag; any BLS cal' in text, "expected to find: " + '- **CGO is required by default** for BLS support (via `github.com/onflow/crypto`). Build with `CGO_ENABLED=1`. You can build with `CGO_ENABLED=0` but must also pass the `no-cgo` build tag; any BLS cal'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When writing portable code, depend on the `access.Client` interface so callers can swap gRPC/HTTP; reach for `grpc.BaseClient` / `http.BaseClient` only when transport-specific options are needed (`a' in text, "expected to find: " + '- When writing portable code, depend on the `access.Client` interface so callers can swap gRPC/HTTP; reach for `grpc.BaseClient` / `http.BaseClient` only when transport-specific options are needed (`a'[:80]

