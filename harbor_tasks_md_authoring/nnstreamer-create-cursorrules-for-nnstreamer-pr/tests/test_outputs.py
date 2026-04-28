"""Behavioral checks for nnstreamer-create-cursorrules-for-nnstreamer-pr (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nnstreamer")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- If tests are not feasible in PR, require a concrete validation procedure (gst-launch snippet, unit test plan).' in text, "expected to find: " + '- If tests are not feasible in PR, require a concrete validation procedure (gst-launch snippet, unit test plan).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- Changes must remain compatible with the Meson build layout (including plugin paths/config expectations).' in text, "expected to find: " + '- Changes must remain compatible with the Meson build layout (including plugin paths/config expectations).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '- If behavior changes or a bug is fixed, recommend adding a regression test or a minimal repro pipeline.' in text, "expected to find: " + '- If behavior changes or a bug is fixed, recommend adding a regression test or a minimal repro pipeline.'[:80]

