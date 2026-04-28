"""Behavioral checks for orbat-mapper-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/orbat-mapper")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'ORBAT Mapper is a client-side web application for building order of battles (ORBATs) and plotting unit locations on maps. It allows users to recreate historic battles and military scenarios in the bro' in text, "expected to find: " + 'ORBAT Mapper is a client-side web application for building order of battles (ORBATs) and plotting unit locations on maps. It allows users to recreate historic battles and military scenarios in the bro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '3. **Performance**: Consider map performance when adding features (large datasets, rendering)' in text, "expected to find: " + '3. **Performance**: Consider map performance when adding features (large datasets, rendering)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '2. **Accessibility**: Ensure UI components are keyboard navigable and screen reader friendly' in text, "expected to find: " + '2. **Accessibility**: Ensure UI components are keyboard navigable and screen reader friendly'[:80]

