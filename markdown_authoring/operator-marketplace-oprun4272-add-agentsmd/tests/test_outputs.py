"""Behavioral checks for operator-marketplace-oprun4272-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/operator-marketplace")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The marketplace-operator enforces software sources for available cluster content, AKA [CatalogSources](https://github.com/operator-framework/api/blob/master/crds/operators.coreos.com_catalogsources.ya' in text, "expected to find: " + 'The marketplace-operator enforces software sources for available cluster content, AKA [CatalogSources](https://github.com/operator-framework/api/blob/master/crds/operators.coreos.com_catalogsources.ya'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '|OperatorHub|`pkg/controller/operatorhub`|Watches the cluster for OperatorHub resources and makes any configured changes to the default CatalogSources, then updates Status of the OperatorHub to show s' in text, "expected to find: " + '|OperatorHub|`pkg/controller/operatorhub`|Watches the cluster for OperatorHub resources and makes any configured changes to the default CatalogSources, then updates Status of the OperatorHub to show s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'To manage on-cluster software sources, marketplace-operator uses the CatalogSource API. A CatalogSource defines a repository of Operators which are served via grpc by the operator-registry. For more i' in text, "expected to find: " + 'To manage on-cluster software sources, marketplace-operator uses the CatalogSource API. A CatalogSource defines a repository of Operators which are served via grpc by the operator-registry. For more i'[:80]

