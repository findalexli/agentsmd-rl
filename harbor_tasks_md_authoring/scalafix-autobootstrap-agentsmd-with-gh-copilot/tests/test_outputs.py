"""Behavioral checks for scalafix-autobootstrap-agentsmd-with-gh-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scalafix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Scalafix is a refactoring and linting tool for Scala. It enables syntactic and semantic source code transformations through a rule-based system. The project targets multiple Scala versions (2.12, 2.13' in text, "expected to find: " + 'Scalafix is a refactoring and linting tool for Scala. It enables syntactic and semantic source code transformations through a rule-based system. The project targets multiple Scala versions (2.12, 2.13'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Pattern**: Test project names combine the Scala version used to compile the test framework with the target being tested: `unit{CompilerVersion}` or `expect{CompilerVersion}Target{TargetVersion}`' in text, "expected to find: " + '**Pattern**: Test project names combine the Scala version used to compile the test framework with the target being tested: `unit{CompilerVersion}` or `expect{CompilerVersion}Target{TargetVersion}`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The build uses `sbt-projectmatrix` to generate multiple sub-projects per module, cross-compiled against different Scala versions. This is NOT standard Scala cross-building.' in text, "expected to find: " + 'The build uses `sbt-projectmatrix` to generate multiple sub-projects per module, cross-compiled against different Scala versions. This is NOT standard Scala cross-building.'[:80]

