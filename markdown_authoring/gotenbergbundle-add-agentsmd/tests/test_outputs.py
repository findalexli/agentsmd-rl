"""Behavioral checks for gotenbergbundle-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gotenbergbundle")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Run `dagger call test --symfony-version '6.4.*' --php-version '8.2' validate-dependencies`" in text, "expected to find: " + "- Run `dagger call test --symfony-version '6.4.*' --php-version '8.2' validate-dependencies`"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `dagger call generate-docs export --path ./docs` to generate the auto API' in text, "expected to find: " + '- Run `dagger call generate-docs export --path ./docs` to generate the auto API'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `dagger call tests-matrix` to test with all supported version of both PHP' in text, "expected to find: " + '- Run `dagger call tests-matrix` to test with all supported version of both PHP'[:80]

