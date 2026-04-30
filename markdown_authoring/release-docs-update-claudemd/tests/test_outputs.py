"""Behavioral checks for release-docs-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/release")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Steps are referenced in `ci-operator/config/` test definitions using multi-stage syntax. The registry allows sharing common operations (cluster provisioning, testing, cleanup) across many repositories' in text, "expected to find: " + 'Steps are referenced in `ci-operator/config/` test definitions using multi-stage syntax. The registry allows sharing common operations (cluster provisioning, testing, cleanup) across many repositories'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This runs: `make jobs`, `make ci-operator-config`, `make prow-config`, `make registry-metadata`, `make release-controllers`, `make boskos-config`' in text, "expected to find: " + 'This runs: `make jobs`, `make ci-operator-config`, `make prow-config`, `make registry-metadata`, `make release-controllers`, `make boskos-config`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Interactive tool to configure CI workflow for a new component repository. Automatically runs `make update` afterwards.' in text, "expected to find: " + 'Interactive tool to configure CI workflow for a new component repository. Automatically runs `make update` afterwards.'[:80]

