"""Behavioral checks for dockerfiles-add-agentsmd-with-containerization-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dockerfiles")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This document provides instructions on how to add a new program to this repository. Following these guidelines ensures consistency, security, and maintainability across all Docker images.' in text, "expected to find: " + 'This document provides instructions on how to add a new program to this repository. Following these guidelines ensures consistency, security, and maintainability across all Docker images.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each program directory must contain a `README.md` with standard badges and usage information. Use the following badge pattern (replace `<program>` with the actual name):' in text, "expected to find: " + 'Each program directory must contain a `README.md` with standard badges and usage information. Use the following badge pattern (replace `<program>` with the actual name):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '[![Build Status](https://github.com/jauderho/dockerfiles/workflows/<program>/badge.svg)](https://github.com/jauderho/dockerfiles/actions)' in text, "expected to find: " + '[![Build Status](https://github.com/jauderho/dockerfiles/workflows/<program>/badge.svg)](https://github.com/jauderho/dockerfiles/actions)'[:80]

