"""Behavioral checks for bnd-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bnd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Bnd/Bndtools is a swiss army knife for OSGi development. It creates manifest headers based on analyzing class code, verifies settings, manages project dependencies, diffs jars, and much more. The repo' in text, "expected to find: " + 'Bnd/Bndtools is a swiss army knife for OSGi development. It creates manifest headers based on analyzing class code, verifies settings, manages project dependencies, diffs jars, and much more. The repo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert './gradlew :build && ./gradlew :gradle-plugins:build && ./.github/scripts/rebuild-build.sh && ./.github/scripts/rebuild-test.sh' in text, "expected to find: " + './gradlew :build && ./gradlew :gradle-plugins:build && ./.github/scripts/rebuild-build.sh && ./.github/scripts/rebuild-test.sh'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Benefits**: Collects all assertion errors instead of stopping at the first one, especially useful for long tests.' in text, "expected to find: " + '**Benefits**: Collects all assertion errors instead of stopping at the first one, especially useful for long tests.'[:80]

