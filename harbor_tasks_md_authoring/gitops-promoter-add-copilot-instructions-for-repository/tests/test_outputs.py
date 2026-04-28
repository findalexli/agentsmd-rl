"""Behavioral checks for gitops-promoter-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gitops-promoter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'GitOps Promoter is a Kubernetes operator that facilitates environment promotion for config managed via GitOps. It provides a drift-free promotion process with a robust gating system, complete integrat' in text, "expected to find: " + 'GitOps Promoter is a Kubernetes operator that facilitates environment promotion for config managed via GitOps. It provides a drift-free promotion process with a robust gating system, complete integrat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '7. **Backwards Compatibility**: While in v1alpha1, breaking changes are allowed but should be avoided if possible' in text, "expected to find: " + '7. **Backwards Compatibility**: While in v1alpha1, breaking changes are allowed but should be avoided if possible'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When adding a new documentation page, update `mkdocs.yml` to include it in the table of contents' in text, "expected to find: " + '- When adding a new documentation page, update `mkdocs.yml` to include it in the table of contents'[:80]

