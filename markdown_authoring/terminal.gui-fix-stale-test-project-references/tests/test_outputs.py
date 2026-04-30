"""Behavioral checks for terminal.gui-fix-stale-test-project-references (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/terminal.gui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See `Tests/README.md` for the full list of test projects (including `IntegrationTests`, `StressTests`, `Benchmarks`) and the static-state classification that determines where a new test belongs.' in text, "expected to find: " + 'See `Tests/README.md` for the full list of test projects (including `IntegrationTests`, `StressTests`, `Benchmarks`) and the static-state classification that determines where a new test belongs.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Add new tests to `UnitTestsParallelizable`; use `UnitTests.NonParallelizable` only when static state is unavoidable. Never add to `UnitTests.Legacy`.' in text, "expected to find: " + '- Add new tests to `UnitTestsParallelizable`; use `UnitTests.NonParallelizable` only when static state is unavoidable. Never add to `UnitTests.Legacy`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'dotnet test --project Tests/UnitTestsParallelizable --no-build --filter "FullyQualifiedName~MyTestClass.MyTestMethod"' in text, "expected to find: " + 'dotnet test --project Tests/UnitTestsParallelizable --no-build --filter "FullyQualifiedName~MyTestClass.MyTestMethod"'[:80]

