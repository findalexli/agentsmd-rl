"""Behavioral checks for openhab-webui-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openhab-webui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains the web user interfaces for the openHAB smart-home project, featuring approximately 5 different extensions located in the `bundles` folder.' in text, "expected to find: " + 'This repository contains the web user interfaces for the openHAB smart-home project, featuring approximately 5 different extensions located in the `bundles` folder.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Important:** This repository depends on the openhab-core repository, which defines the base system and APIs.' in text, "expected to find: " + '**Important:** This repository depends on the openhab-core repository, which defines the base system and APIs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'There might be AGENTS.md files in subfolders. Consider them when files from that UI are open in the editor:' in text, "expected to find: " + 'There might be AGENTS.md files in subfolders. Consider them when files from that UI are open in the editor:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('bundles/org.openhab.ui/AGENTS.md')
    assert '- Write unit tests for utilities, and composables where appropriate. Focus on testing logic and behavior rather than implementation details. Store tests alongside the code they test, using the `.test.' in text, "expected to find: " + '- Write unit tests for utilities, and composables where appropriate. Focus on testing logic and behavior rather than implementation details. Store tests alongside the code they test, using the `.test.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('bundles/org.openhab.ui/AGENTS.md')
    assert '- **Reactivity export reactivity:** Composables must not export raw values. Instead, they should export `Ref`s or `ComputedRef`s to ensure reactivity is preserved for the caller.' in text, "expected to find: " + '- **Reactivity export reactivity:** Composables must not export raw values. Instead, they should export `Ref`s or `ComputedRef`s to ensure reactivity is preserved for the caller.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('bundles/org.openhab.ui/AGENTS.md')
    assert '- **Composable argument reactivity:** If reactivity needs to be preserved when passing arguments to composables, `Ref`s or `ComputedRef`s must be passed instead of raw values.' in text, "expected to find: " + '- **Composable argument reactivity:** If reactivity needs to be preserved when passing arguments to composables, `Ref`s or `ComputedRef`s must be passed instead of raw values.'[:80]

