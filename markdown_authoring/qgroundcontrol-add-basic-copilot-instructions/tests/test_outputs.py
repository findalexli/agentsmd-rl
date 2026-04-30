"""Behavioral checks for qgroundcontrol-add-basic-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qgroundcontrol")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'QGroundControl (QGC) is an intuitive and powerful Ground Control Station (GCS) for UAVs. It provides comprehensive flight control and mission planning for MAVLink-enabled drones, with full support for' in text, "expected to find: " + 'QGroundControl (QGC) is an intuitive and powerful Ground Control Station (GCS) for UAVs. It provides comprehensive flight control and mission planning for MAVLink-enabled drones, with full support for'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**State types:** `DelayState`, `FunctionState`, `SendMavlinkCommandState`, `WaitForMavlinkMessageState`, `ShowAppMessageState`' in text, "expected to find: " + '**State types:** `DelayState`, `FunctionState`, `SendMavlinkCommandState`, `WaitForMavlinkMessageState`, `ShowAppMessageState`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. See [Developer Guide](https://dev.qgroundcontrol.com/en/getting_started/) for detailed build instructions' in text, "expected to find: " + '4. See [Developer Guide](https://dev.qgroundcontrol.com/en/getting_started/) for detailed build instructions'[:80]

