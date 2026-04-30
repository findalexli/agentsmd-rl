"""Behavioral checks for scribe-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scribe")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Strict Types**: Do **NOT** use `declare(strict_types=1);` unless strictly necessary or found in the file being edited (it is generally absent).' in text, "expected to find: " + '- **Strict Types**: Do **NOT** use `declare(strict_types=1);` unless strictly necessary or found in the file being edited (it is generally absent).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `/** @var ClassName $var */` for inline type hinting when the static analyzer cannot infer it (e.g., resolving from container).' in text, "expected to find: " + '- Use `/** @var ClassName $var */` for inline type hinting when the static analyzer cannot infer it (e.g., resolving from container).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Framework**: Tests are written using PHPUnit class syntax (extending `BaseLaravelTest` or `TestCase`), but executed via Pest.' in text, "expected to find: " + '- **Framework**: Tests are written using PHPUnit class syntax (extending `BaseLaravelTest` or `TestCase`), but executed via Pest.'[:80]

