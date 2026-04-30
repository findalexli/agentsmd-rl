"""Behavioral checks for mc_mujoco-create-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mc-mujoco")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "mc_mujoco is a MuJoCo simulator interface for mc_rtc (a robotics control framework). It bridges MuJoCo physics simulation with mc_rtc's controller system, allowing FSM controllers to run in MuJoCo wit" in text, "expected to find: " + "mc_mujoco is a MuJoCo simulator interface for mc_rtc (a robotics control framework). It bridges MuJoCo physics simulation with mc_rtc's controller system, allowing FSM controllers to run in MuJoCo wit"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **States** — FSM building blocks with lifecycle: construct → init → run (until done) → teardown → destruct. Loaded dynamically from shared libraries via `StateFactory`. Registered with `EXPORT_SINGL' in text, "expected to find: " + '- **States** — FSM building blocks with lifecycle: construct → init → run (until done) → teardown → destruct. Loaded dynamically from shared libraries via `StateFactory`. Registered with `EXPORT_SINGL'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **MCGlobalController** — Top-level controller manager. Handles sensor data, loads controllers dynamically, manages plugins and observers. mc_mujoco instantiates this to run mc_rtc controllers agains' in text, "expected to find: " + '- **MCGlobalController** — Top-level controller manager. Handles sensor data, loads controllers dynamically, manages plugins and observers. mc_mujoco instantiates this to run mc_rtc controllers agains'[:80]

