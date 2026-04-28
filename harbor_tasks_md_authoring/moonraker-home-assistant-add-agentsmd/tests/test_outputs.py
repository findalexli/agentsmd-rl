"""Behavioral checks for moonraker-home-assistant-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/moonraker-home-assistant")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Core integration code sits in `custom_components/moonraker/`: Home Assistant boots through `__init__.py`, entity platforms like `sensor.py`, `camera.py`, and `switch.py` expose printer features, while' in text, "expected to find: " + 'Core integration code sits in `custom_components/moonraker/`: Home Assistant boots through `__init__.py`, entity platforms like `sensor.py`, `camera.py`, and `switch.py` expose printer features, while'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Place tests beside their feature under `tests/` and name files `test_<feature>.py`. Reuse fixtures in `tests/conftest.py` for mocked Moonraker clients; assert on Home Assistant states rather than raw ' in text, "expected to find: " + 'Place tests beside their feature under `tests/` and name files `test_<feature>.py`. Reuse fixtures in `tests/conftest.py` for mocked Moonraker clients; assert on Home Assistant states rather than raw '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Target Python 3.13 with four-space indentation. Follow Home Assistant norms: modules and entities in snake_case, user-facing strings sentence case, constants upper snake in `const.py`, and translation' in text, "expected to find: " + 'Target Python 3.13 with four-space indentation. Follow Home Assistant norms: modules and entities in snake_case, user-facing strings sentence case, constants upper snake in `const.py`, and translation'[:80]

