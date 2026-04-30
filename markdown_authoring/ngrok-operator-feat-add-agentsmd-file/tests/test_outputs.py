"""Behavioral checks for ngrok-operator-feat-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ngrok-operator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **BaseController** ([internal/controller/base_controller.go](internal/controller/base_controller.go)) - Common CRUD operations, finalizer management, status updates' in text, "expected to find: " + '- **BaseController** ([internal/controller/base_controller.go](internal/controller/base_controller.go)) - Common CRUD operations, finalizer management, status updates'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **gateway.networking.k8s.io/v1** | Gateway, GatewayClass, HTTPRoute, TLSRoute, TCPRoute | [internal/controller/gateway/](internal/controller/gateway/) |' in text, "expected to find: " + '| **gateway.networking.k8s.io/v1** | Gateway, GatewayClass, HTTPRoute, TLSRoute, TCPRoute | [internal/controller/gateway/](internal/controller/gateway/) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **bindings.k8s.ngrok.com/v1alpha1** | BindingConfiguration, BoundEndpoint | [internal/controller/bindings/](internal/controller/bindings/) |' in text, "expected to find: " + '| **bindings.k8s.ngrok.com/v1alpha1** | BindingConfiguration, BoundEndpoint | [internal/controller/bindings/](internal/controller/bindings/) |'[:80]

