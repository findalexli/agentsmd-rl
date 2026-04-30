"""Behavioral checks for zigbee2mqtt-chore-update-agentsmd-and-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/zigbee2mqtt")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Private members**: Prefix with underscore for private class fields only when needed to distinguish from public properties (e.g., `_definitionModelID`)' in text, "expected to find: " + '- **Private members**: Prefix with underscore for private class fields only when needed to distinguish from public properties (e.g., `_definitionModelID`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '4. **Architectural Consistency**: Maintain our layered architectural style with clear separation between controller, extensions, models, and utilities' in text, "expected to find: " + '4. **Architectural Consistency**: Maintain our layered architectural style with clear separation between controller, extensions, models, and utilities'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Version Compatibility**: Always detect and respect the exact versions of languages, frameworks, and libraries used in this project' in text, "expected to find: " + '1. **Version Compatibility**: Always detect and respect the exact versions of languages, frameworks, and libraries used in this project'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Zigbee2MQTT is a Zigbee to MQTT bridge that allows you to use your Zigbee devices without the vendor's bridge or gateway. It bridges events and allows you to control Zigbee devices via MQTT, integrati" in text, "expected to find: " + "Zigbee2MQTT is a Zigbee to MQTT bridge that allows you to use your Zigbee devices without the vendor's bridge or gateway. It bridges events and allows you to control Zigbee devices via MQTT, integrati"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The Controller instantiates and injects dependencies into all extensions. Follow this pattern when creating new extensions.' in text, "expected to find: " + 'The Controller instantiates and injects dependencies into all extensions. Follow this pattern when creating new extensions.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Important**: Device support is NOT added to this repository. All device definitions live in `zigbee-herdsman-converters`.' in text, "expected to find: " + '**Important**: Device support is NOT added to this repository. All device definitions live in `zigbee-herdsman-converters`.'[:80]

