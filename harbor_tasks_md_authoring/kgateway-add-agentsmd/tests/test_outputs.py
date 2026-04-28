"""Behavioral checks for kgateway-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kgateway")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Instead, run your tests with environment variable `REFRESH_GOLDEN=true` For example: `REFRESH_GOLDEN=true go test -timeout 30s -run ^TestBasic$/^ListenerPolicy_with_proxy_protocol_on_HTTPS_listener$ g' in text, "expected to find: " + 'Instead, run your tests with environment variable `REFRESH_GOLDEN=true` For example: `REFRESH_GOLDEN=true go test -timeout 30s -run ^TestBasic$/^ListenerPolicy_with_proxy_protocol_on_HTTPS_listener$ g'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "kgateway is a **dual control plane** implementing the Kubernetes Gateway API for both Envoy and agentgateway. It's built on KRT (Kubernetes Declarative Controller Runtime from Istio) and uses a plugin" in text, "expected to find: " + "kgateway is a **dual control plane** implementing the Kubernetes Gateway API for both Envoy and agentgateway. It's built on KRT (Kubernetes Declarative Controller Runtime from Istio) and uses a plugin"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. Create `*_types.go` in `api/v1alpha1/` with `+kubebuilder` markers. You can use `+kubebuilder:validation:AtLeastOneOf` or `+kubebuilder:validation:ExactlyOneOf` for field groups.' in text, "expected to find: " + '1. Create `*_types.go` in `api/v1alpha1/` with `+kubebuilder` markers. You can use `+kubebuilder:validation:AtLeastOneOf` or `+kubebuilder:validation:ExactlyOneOf` for field groups.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

