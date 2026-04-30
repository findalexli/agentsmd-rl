"""Behavioral checks for helm-charts-create-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/helm-charts")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Pull Requests against this repository require that all charts which implement helm-docs(https://github.com/norwoodj/helm-docs) must re-generate their README.md files after modifying `values.yaml` or `' in text, "expected to find: " + 'Pull Requests against this repository require that all charts which implement helm-docs(https://github.com/norwoodj/helm-docs) must re-generate their README.md files after modifying `values.yaml` or `'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Renovate manages automated dependency updates. Charts with subchart dependencies (e.g., `tempo-distributed` depends on `minio`, `grafana-agent-operator`, `rollout-operator`) declare them in `Chart.yam' in text, "expected to find: " + 'Renovate manages automated dependency updates. Charts with subchart dependencies (e.g., `tempo-distributed` depends on `minio`, `grafana-agent-operator`, `rollout-operator`) declare them in `Chart.yam'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Pull Requests against this repository require that all charts which implement helm-unittests(https://github.com/norwoodj/helm-docs) must pass all of their unittests.  This can be done via a single com' in text, "expected to find: " + 'Pull Requests against this repository require that all charts which implement helm-unittests(https://github.com/norwoodj/helm-docs) must pass all of their unittests.  This can be done via a single com'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

