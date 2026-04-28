"""Behavioral checks for gridlayout-compose-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gridlayout-compose")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Update documentation when the feature is added, removed or changed.' in text, "expected to find: " + '- Update documentation when the feature is added, removed or changed.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `./gradlew recordPaparazziDebug`: Update and create new snapshots.' in text, "expected to find: " + '- `./gradlew recordPaparazziDebug`: Update and create new snapshots.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `./gradlew apiDump`: Update public API binary compatibility.' in text, "expected to find: " + '- `./gradlew apiDump`: Update public API binary compatibility.'[:80]

