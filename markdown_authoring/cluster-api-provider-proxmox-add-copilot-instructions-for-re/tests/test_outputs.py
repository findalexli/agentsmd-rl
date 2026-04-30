"""Behavioral checks for cluster-api-provider-proxmox-add-copilot-instructions-for-re (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cluster-api-provider-proxmox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'CAPMOX is a Kubernetes Cluster API provider that enables declarative management of Kubernetes clusters on Proxmox VE infrastructure. It follows the Kubernetes Operator pattern and uses controllers to ' in text, "expected to find: " + 'CAPMOX is a Kubernetes Cluster API provider that enables declarative management of Kubernetes clusters on Proxmox VE infrastructure. It follows the Kubernetes Operator pattern and uses controllers to '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `api/v1alpha1/` - Custom Resource Definitions (ProxmoxCluster, ProxmoxMachine, ProxmoxMachineTemplate, ProxmoxClusterTemplate)' in text, "expected to find: " + '- `api/v1alpha1/` - Custom Resource Definitions (ProxmoxCluster, ProxmoxMachine, ProxmoxMachineTemplate, ProxmoxClusterTemplate)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Test Failures**: Run `make test` to see detailed error messages. Unit tests use envtest with Kubernetes 1.30.0.' in text, "expected to find: " + '1. **Test Failures**: Run `make test` to see detailed error messages. Unit tests use envtest with Kubernetes 1.30.0.'[:80]

