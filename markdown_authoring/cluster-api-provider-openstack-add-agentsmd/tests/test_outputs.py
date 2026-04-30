"""Behavioral checks for cluster-api-provider-openstack-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cluster-api-provider-openstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **⚠️ IMPORTANT**: When making changes to Makefile targets, PR requirements, code generation workflows, verification steps, or any other information referenced in this document, **AGENTS.md must be u' in text, "expected to find: " + '> **⚠️ IMPORTANT**: When making changes to Makefile targets, PR requirements, code generation workflows, verification steps, or any other information referenced in this document, **AGENTS.md must be u'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Cluster API Provider OpenStack (CAPO) is a Kubernetes-native declarative infrastructure provider for managing Kubernetes clusters on OpenStack. It implements the Cluster API (CAPI) specification for s' in text, "expected to find: " + 'Cluster API Provider OpenStack (CAPO) is a Kubernetes-native declarative infrastructure provider for managing Kubernetes clusters on OpenStack. It implements the Cluster API (CAPI) specification for s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document provides guidelines and useful commands for AI agents contributing to the Cluster API Provider OpenStack (CAPO) repository.' in text, "expected to find: " + 'This document provides guidelines and useful commands for AI agents contributing to the Cluster API Provider OpenStack (CAPO) repository.'[:80]

