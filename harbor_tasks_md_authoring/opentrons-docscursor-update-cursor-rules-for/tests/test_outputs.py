"""Behavioral checks for opentrons-docscursor-update-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opentrons")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert '- CSS file names should be `snake_case` and match the component name, followed by `.module.css`.' in text, "expected to find: " + '- CSS file names should be `snake_case` and match the component name, followed by `.module.css`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert '- This repo uses `clsx` (https://github.com/lukeed/clsx) for conditionally applying classes.' in text, "expected to find: " + '- This repo uses `clsx` (https://github.com/lukeed/clsx) for conditionally applying classes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/css-modules.mdc')
    assert '- Example: `navbar.module.css`, `primary_button.module.css`, `modal_shell.module.css`' in text, "expected to find: " + '- Example: `navbar.module.css`, `primary_button.module.css`, `modal_shell.module.css`'[:80]

