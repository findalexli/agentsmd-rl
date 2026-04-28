"""Behavioral checks for julia-agentsmd-expand-revise-example (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/julia")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'JULIA_TEST_FAILFAST=1 ./julia -e \'using Revise; Revise.track(Base); include("test.jl")\'' in text, "expected to find: " + 'JULIA_TEST_FAILFAST=1 ./julia -e \'using Revise; Revise.track(Base); include("test.jl")\''[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'For instance testing Base changes without rebuilding, using failfast, you can run:' in text, "expected to find: " + 'For instance testing Base changes without rebuilding, using failfast, you can run:'[:80]

