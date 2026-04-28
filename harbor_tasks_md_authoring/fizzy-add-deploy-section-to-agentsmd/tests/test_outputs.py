"""Behavioral checks for fizzy-add-deploy-section-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fizzy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Note: `beta` is a template requiring `BETA_NUMBER` env var; typical targets are `beta1`-`beta4`.' in text, "expected to find: " + 'Note: `beta` is a template requiring `BETA_NUMBER` env var; typical targets are `beta1`-`beta4`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Destinations: production, staging, beta, beta1, beta2, beta3, beta4' in text, "expected to find: " + 'Destinations: production, staging, beta, beta1, beta2, beta3, beta4'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Deploy: `bin/kamal deploy -d <destination>`' in text, "expected to find: " + 'Deploy: `bin/kamal deploy -d <destination>`'[:80]

