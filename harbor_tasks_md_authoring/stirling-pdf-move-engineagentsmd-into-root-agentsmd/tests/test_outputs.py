"""Behavioral checks for stirling-pdf-move-engineagentsmd-into-root-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stirling-pdf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The engine is a Python reasoning service for Stirling: it plans and interprets work, but it does not own durable state, and it does not execute Stirling PDF operations directly. Keep the service narro' in text, "expected to find: " + 'The engine is a Python reasoning service for Stirling: it plans and interprets work, but it does not own durable state, and it does not execute Stirling PDF operations directly. Keep the service narro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do not require the model to keep separate structures in sync. For example, instead of generating two lists which must be the same length, generate one list of a model containing the same data.' in text, "expected to find: " + '- Do not require the model to keep separate structures in sync. For example, instead of generating two lists which must be the same length, generate one list of a model containing the same data.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The system must work with any AI, including self-hosted models. We require that the models support structured outputs, but should minimise model-specific code beyond that.' in text, "expected to find: " + '- The system must work with any AI, including self-hosted models. We require that the models support structured outputs, but should minimise model-specific code beyond that.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('engine/AGENTS.md')
    assert 'engine/AGENTS.md' in text, "expected to find: " + 'engine/AGENTS.md'[:80]

