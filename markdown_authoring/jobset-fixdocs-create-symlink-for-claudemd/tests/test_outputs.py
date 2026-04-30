"""Behavioral checks for jobset-fixdocs-create-symlink-for-claudemd (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '- **Validation**: Use [CEL validation](https://kubernetes.io/docs/reference/using-api/cel/) (`+kubebuilder:validation:XValidation`) wherever applicable instead of webhook-only validation' in text, "expected to find: " + '- **Validation**: Use [CEL validation](https://kubernetes.io/docs/reference/using-api/cel/) (`+kubebuilder:validation:XValidation`) wherever applicable instead of webhook-only validation'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow the [Kubernetes commit message convention](https://www.kubernetes.dev/docs/guide/pull-requests/#commit-message-guidelines):' in text, "expected to find: " + '- Follow the [Kubernetes commit message convention](https://www.kubernetes.dev/docs/guide/pull-requests/#commit-message-guidelines):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Removing or renaming fields**: Requires an API version bump and a migration plan — do not do this without explicit instruction' in text, "expected to find: " + '- **Removing or renaming fields**: Requires an API version bump and a migration plan — do not do this without explicit instruction'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

