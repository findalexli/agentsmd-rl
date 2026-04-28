"""Behavioral checks for united-manufacturing-hub-docs-add-fsm-troubleshooting-workfl (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/united-manufacturing-hub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Resource limiting**: Controlled by `agent.enableResourceLimitBlocking` and related settings. Default: ≤70% CPU; ~5 bridges per CPU core after reserving 1 for Redpanda' in text, "expected to find: " + '- **Resource limiting**: Controlled by `agent.enableResourceLimitBlocking` and related settings. Default: ≤70% CPU; ~5 bridges per CPU core after reserving 1 for Redpanda'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Resource Limiting**: Bridge creation is blocked when resources are constrained (controlled by `agent.enableResourceLimitBlocking` feature flag)' in text, "expected to find: " + '- **Resource Limiting**: Bridge creation is blocked when resources are constrained (controlled by `agent.enableResourceLimitBlocking` feature flag)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**MUST run before completing tasks**: `golangci-lint run`, `go vet ./...`, check no focused tests with `ginkgo -r --fail-on-focused`' in text, "expected to find: " + '**MUST run before completing tasks**: `golangci-lint run`, `go vet ./...`, check no focused tests with `ginkgo -r --fail-on-focused`'[:80]

