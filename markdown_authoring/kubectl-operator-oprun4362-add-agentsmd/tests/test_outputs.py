"""Behavioral checks for kubectl-operator-oprun4362-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kubectl-operator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**kubectl-operator** is a kubectl plugin that functions as a package manager for OLM Operators. It provides a CLI interface for managing both OLMv0 operators (legacy, through [Subscriptions](https://g' in text, "expected to find: " + '**kubectl-operator** is a kubectl plugin that functions as a package manager for OLM Operators. It provides a CLI interface for managing both OLMv0 operators (legacy, through [Subscriptions](https://g'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **ClusterCatalog** | olm.operatorframework.io/v1 | Catalog definition pointing to FBC (File-Based Catalog) image | Created by `olmv1 create catalog`, queried by `olmv1 get catalogs` and `olmv1 searc' in text, "expected to find: " + '| **ClusterCatalog** | olm.operatorframework.io/v1 | Catalog definition pointing to FBC (File-Based Catalog) image | Created by `olmv1 create catalog`, queried by `olmv1 get catalogs` and `olmv1 searc'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **ClusterExtension** | olm.operatorframework.io/v1alpha1 | Desired state of an installed operator/extension on the cluster | Created by `olmv1 install extension`, queried by `olmv1 get extensions`, ' in text, "expected to find: " + '| **ClusterExtension** | olm.operatorframework.io/v1alpha1 | Desired state of an installed operator/extension on the cluster | Created by `olmv1 install extension`, queried by `olmv1 get extensions`, '[:80]

