"""Behavioral checks for ert-expand-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ert")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Plugin system lives under `src/ert/plugins` (hook specs + implementations + runtime plugin loading); `ert.__main__` executes within runtime plugin context.' in text, "expected to find: " + '- Plugin system lives under `src/ert/plugins` (hook specs + implementations + runtime plugin loading); `ert.__main__` executes within runtime plugin context.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Keep unit tests in `tests/ert/unit_tests` exceptionally fast; slower/broader cases should be marked with `@pytest.mark.integration_test` or moved.' in text, "expected to find: " + '- Keep unit tests in `tests/ert/unit_tests` exceptionally fast; slower/broader cases should be marked with `@pytest.mark.integration_test` or moved.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Pre-commit is the source of truth for formatting/lint hooks (`ruff-check --fix`, `ruff-format`, yaml/json checks, actionlint, lockfile checks).' in text, "expected to find: " + '- Pre-commit is the source of truth for formatting/lint hooks (`ruff-check --fix`, `ruff-format`, yaml/json checks, actionlint, lockfile checks).'[:80]

