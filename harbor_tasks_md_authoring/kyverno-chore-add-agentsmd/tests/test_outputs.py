"""Behavioral checks for kyverno-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kyverno")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Kyverno is a Kubernetes-native policy engine for security, compliance, automation, and governance through policy-as-code. It validates, mutates, generates, and cleans up Kubernetes resources using adm' in text, "expected to find: " + 'Kyverno is a Kubernetes-native policy engine for security, compliance, automation, and governance through policy-as-code. It validates, mutates, generates, and cleans up Kubernetes resources using adm'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Linting is configured via `.golangci.yml` (golangci-lint v2). Enabled linters include `gosec`, `misspell`, `paralleltest`, `unconvert`, `errname`, `importas`, and others. The `importas` linter enforce' in text, "expected to find: " + 'Linting is configured via `.golangci.yml` (golangci-lint v2). Enabled linters include `gosec`, `misspell`, `paralleltest`, `unconvert`, `errname`, `importas`, and others. The `importas` linter enforce'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Admission Controller** (`cmd/kyverno/`): The core component. Receives AdmissionReview requests, evaluates validate/mutate rules synchronously, and queues generate/audit rules for async processing.' in text, "expected to find: " + '- **Admission Controller** (`cmd/kyverno/`): The core component. Receives AdmissionReview requests, evaluates validate/mutate rules synchronously, and queues generate/audit rules for async processing.'[:80]

