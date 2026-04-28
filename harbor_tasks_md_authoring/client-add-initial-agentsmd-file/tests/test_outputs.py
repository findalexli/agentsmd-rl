"""Behavioral checks for client-add-initial-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/client")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The Knative client `kn` is a CLI tool for managing Knative Serving and Eventing resources. It provides a kubectl-plugin-like architecture with full support for Knative Serving (services, revisions, tr' in text, "expected to find: " + 'The Knative client `kn` is a CLI tool for managing Knative Serving and Eventing resources. It provides a kubectl-plugin-like architecture with full support for Knative Serving (services, revisions, tr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a Go-based project (Go 1.24.2+) that uses Cobra for CLI commands and interacts with Kubernetes clusters via client-go.' in text, "expected to find: " + 'This is a Go-based project (Go 1.24.2+) that uses Cobra for CLI commands and interacts with Kubernetes clusters via client-go.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `pkg/serving/v1/client.go`: Interface `KnServingClient` for Serving resources (services, revisions, routes)' in text, "expected to find: " + '- `pkg/serving/v1/client.go`: Interface `KnServingClient` for Serving resources (services, revisions, routes)'[:80]

