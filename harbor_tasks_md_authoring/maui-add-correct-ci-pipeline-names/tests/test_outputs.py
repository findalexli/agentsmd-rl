"""Behavioral checks for maui-add-correct-ci-pipeline-names (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/maui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**⚠️ Old pipeline names** (e.g., `MAUI-UITests-public`, `MAUI-public`) are **outdated** and should NOT be used. Always use the names above.' in text, "expected to find: " + '**⚠️ Old pipeline names** (e.g., `MAUI-UITests-public`, `MAUI-public`) are **outdated** and should NOT be used. Always use the names above.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'When referencing or triggering CI pipelines, use these current pipeline names:' in text, "expected to find: " + 'When referencing or triggering CI pipelines, use these current pipeline names:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| Device Tests | `maui-pr-devicetests` | Helix-based device tests |' in text, "expected to find: " + '| Device Tests | `maui-pr-devicetests` | Helix-based device tests |'[:80]

