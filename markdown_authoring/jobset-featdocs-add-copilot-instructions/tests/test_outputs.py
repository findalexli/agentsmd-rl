"""Behavioral checks for jobset-featdocs-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jobset")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'JobSet presubmit tests are defined here: https://github.com/kubernetes/test-infra/blob/master/config/jobs/kubernetes-sigs/jobset/jobset-presubmit-main.yaml' in text, "expected to find: " + 'JobSet presubmit tests are defined here: https://github.com/kubernetes/test-infra/blob/master/config/jobs/kubernetes-sigs/jobset/jobset-presubmit-main.yaml'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Violating [Kubernetes API guidelines](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api_changes.md)' in text, "expected to find: " + '- Violating [Kubernetes API guidelines](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api_changes.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "If you're uncertain whether something is an issue, don't comment. False positives create noise and reduce trust in the review process." in text, "expected to find: " + "If you're uncertain whether something is an issue, don't comment. False positives create noise and reduce trust in the review process."[:80]

