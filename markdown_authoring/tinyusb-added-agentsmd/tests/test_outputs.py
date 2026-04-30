"""Behavioral checks for tinyusb-added-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tinyusb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Match file organization: core stack under `src`, MCU/BSP support in `hw/{mcu,bsp}`, examples under `examples/{device,host,dual}`, docs in `docs`, tests under `test/{unit-test,fuzz,hil}`.' in text, "expected to find: " + '- Match file organization: core stack under `src`, MCU/BSP support in `hw/{mcu,bsp}`, examples under `examples/{device,host,dual}`, docs in `docs`, tests under `test/{unit-test,fuzz,hil}`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Release flow primer: bump `tools/make_release.py` version, run the script (updates `src/tusb_option.h`, `repository.yml`, `library.json`), refresh `docs/info/changelog.rst`, then tag.' in text, "expected to find: " + '- Release flow primer: bump `tools/make_release.py` version, run the script (updates `src/tusb_option.h`, `repository.yml`, `library.json`), refresh `docs/info/changelog.rst`, then tag.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use descriptive snake_case for helpers, reserve `tud_`/`tuh_` for public APIs, `TU_` for macros, and keep headers self-contained with `#if CFG_TUSB_MCU` guards where needed.' in text, "expected to find: " + '- Use descriptive snake_case for helpers, reserve `tud_`/`tuh_` for public APIs, `TU_` for macros, and keep headers self-contained with `#if CFG_TUSB_MCU` guards where needed.'[:80]

