"""Behavioral checks for policy-collection-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/policy-collection")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This is the **policy-collection** repository for Open Cluster Management (OCM). It contains a collection of governance policies that can be deployed to Kubernetes/OpenShift clusters through OCM's poli" in text, "expected to find: " + "This is the **policy-collection** repository for Open Cluster Management (OCM). It contains a collection of governance policies that can be deployed to Kubernetes/OpenShift clusters through OCM's poli"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Important**: You must be a Subscription Administrator. Add yourself to the `open-cluster-management:subscription-admin` ClusterRoleBinding if needed.' in text, "expected to find: " + '**Important**: You must be a Subscription Administrator. Add yourself to the `open-cluster-management:subscription-admin` ClusterRoleBinding if needed.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The Policy Generator is a Kustomize plugin that automatically wraps Kubernetes manifests in OCM policies. Key features:' in text, "expected to find: " + 'The Policy Generator is a Kustomize plugin that automatically wraps Kubernetes manifests in OCM policies. Key features:'[:80]

