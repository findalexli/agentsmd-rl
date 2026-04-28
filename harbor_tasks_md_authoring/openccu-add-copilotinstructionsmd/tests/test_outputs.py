"""Behavioral checks for openccu-add-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openccu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '`scripts/update-*.sh` scripts automate upstream component bumps. Tracked components include Buildroot, the RPi and ODROID/Tinkerboard kernels, RPi firmware/EEPROM, Java Azul, CloudMatic, CodeMirror (W' in text, "expected to find: " + '`scripts/update-*.sh` scripts automate upstream component bumps. Tracked components include Buildroot, the RPi and ODROID/Tinkerboard kernels, RPi firmware/EEPROM, Java Azul, CloudMatic, CodeMirror (W'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Version pins for packages sourced from GitHub use **commit SHAs** (not tag names) for `generic_raw_uart`, `detect_radio_module`, `cloudmatic`, `hardkernel-boot`, `picod`, `raspi-fanshim`, and `wirin' in text, "expected to find: " + '- Version pins for packages sourced from GitHub use **commit SHAs** (not tag names) for `generic_raw_uart`, `detect_radio_module`, `cloudmatic`, `hardkernel-boot`, `picod`, `raspi-fanshim`, and `wirin'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The recovery build **reuses already-built multilib32 artifacts** via rsync rather than rebuilding them. The `RECOVERY_SYSTEM_CONFIGURE_CMDS` step copies any `multilib32-*` build directories from the o' in text, "expected to find: " + 'The recovery build **reuses already-built multilib32 artifacts** via rsync rather than rebuilding them. The `RECOVERY_SYSTEM_CONFIGURE_CMDS` step copies any `multilib32-*` build directories from the o'[:80]

