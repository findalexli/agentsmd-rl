"""Behavioral checks for trucksim-telemetry-create-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/trucksim-telemetry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Data Conversion:** When adding support for a new version of the `scs-sdk-plugin`, a new file should be created in `lib/converter/`. This file will be responsible for converting the new data struct' in text, "expected to find: " + '- **Data Conversion:** When adding support for a new version of the `scs-sdk-plugin`, a new file should be created in `lib/converter/`. This file will be responsible for converting the new data struct'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Event Emitters:** Event emitters in `lib/eventEmitters/` are responsible for watching for specific data changes and emitting events. They should be self-contained and focus on a specific domain of' in text, "expected to find: " + '- **Event Emitters:** Event emitters in `lib/eventEmitters/` are responsible for watching for specific data changes and emitting events. They should be self-contained and focus on a specific domain of'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This project is a Node.js module with a native C++ addon for reading telemetry data from the games Euro Truck Simulator 2 and American Truck Simulator. The data is provided by the `scs-sdk-plugin` via' in text, "expected to find: " + 'This project is a Node.js module with a native C++ addon for reading telemetry data from the games Euro Truck Simulator 2 and American Truck Simulator. The data is provided by the `scs-sdk-plugin` via'[:80]

