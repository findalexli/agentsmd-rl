"""Behavioral checks for authorino-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/authorino")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Authorino is a Kubernetes-native authorization service that implements Envoy's external authorization gRPC protocol. It acts as an authorization layer between Envoy proxy and upstream services, provid" in text, "expected to find: " + "Authorino is a Kubernetes-native authorization service that implements Envoy's external authorization gRPC protocol. It acts as an authorization layer between Envoy proxy and upstream services, provid"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Authorization JSON**: Working memory for each request containing `context` (request data from Envoy) and `auth` (resolved identity, metadata, authorization results). Evaluators read/write from this ' in text, "expected to find: " + '**Authorization JSON**: Working memory for each request containing `context` (request data from Envoy) and `auth` (resolved identity, metadata, authorization results). Evaluators read/write from this '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Tests use envtest (Kubernetes control plane components) for controller tests. Set `KUBEBUILDER_ASSETS` to the envtest binaries path (handled by `make test`).' in text, "expected to find: " + 'Tests use envtest (Kubernetes control plane components) for controller tests. Set `KUBEBUILDER_ASSETS` to the envtest binaries path (handled by `make test`).'[:80]

