"""Behavioral checks for azerothcore-wotlk-docs-init-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azerothcore-wotlk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'External modules are loaded from the `modules/` directory. Each module is a subdirectory with its own `CMakeLists.txt`. Disable specific modules with `-DDISABLED_AC_MODULES="mod1;mod2"`. Module skelet' in text, "expected to find: " + 'External modules are loaded from the `modules/` directory. Each module is a subdirectory with its own `CMakeLists.txt`. Disable specific modules with `-DDISABLED_AC_MODULES="mod1;mod2"`. Module skelet'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "AzerothCore is an open-source MMORPG server emulator for World of Warcraft patch 3.3.5a (Wrath of the Lich King). It's a C++ project built with CMake, using MySQL for data storage. Licensed under GNU " in text, "expected to find: " + "AzerothCore is an open-source MMORPG server emulator for World of Warcraft patch 3.3.5a (Wrath of the Lich King). It's a C++ project built with CMake, using MySQL for data storage. Licensed under GNU "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Scripting/** - Script system with typed base classes (`ScriptObject` subclasses: `CreatureScript`, `SpellScript`, `InstanceMapScript`, `GameObjectScript`, `CommandScript`, etc.)' in text, "expected to find: " + '- **Scripting/** - Script system with typed base classes (`ScriptObject` subclasses: `CreatureScript`, `SpellScript`, `InstanceMapScript`, `GameObjectScript`, `CommandScript`, etc.)'[:80]

