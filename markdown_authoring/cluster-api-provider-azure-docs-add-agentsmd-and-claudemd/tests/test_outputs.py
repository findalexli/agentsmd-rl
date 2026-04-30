"""Behavioral checks for cluster-api-provider-azure-docs-add-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cluster-api-provider-azure")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Cluster API Provider Azure (CAPZ) is a Kubernetes-native declarative infrastructure provider for managing Azure clusters. It implements the Cluster API (CAPI) specification for both self-managed (IaaS' in text, "expected to find: " + 'Cluster API Provider Azure (CAPZ) is a Kubernetes-native declarative infrastructure provider for managing Azure clusters. It implements the Cluster API (CAPI) specification for both self-managed (IaaS'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**tilt-settings.yaml** is required with Azure credentials (see docs/book/src/developers/development.md for details).' in text, "expected to find: " + '**tilt-settings.yaml** is required with Azure credentials (see docs/book/src/developers/development.md for details).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'KUBEBUILDER_ASSETS="$(make setup-envtest 2>&1 | grep -o \'/.*\')" go test -v -run TestFunctionName ./path/to/package' in text, "expected to find: " + 'KUBEBUILDER_ASSETS="$(make setup-envtest 2>&1 | grep -o \'/.*\')" go test -v -run TestFunctionName ./path/to/package'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

