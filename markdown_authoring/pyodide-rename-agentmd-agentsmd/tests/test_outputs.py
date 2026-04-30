"""Behavioral checks for pyodide-rename-agentmd-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pyodide")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '.cursorrules' in text, "expected to find: " + '.cursorrules'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **pyodide-build/:** Contains the build system for Pyodide. pyodide-build is a submodule and we do not directly modify the source code in this repository. All the pyodide-build-related changes should' in text, "expected to find: " + '- **pyodide-build/:** Contains the build system for Pyodide. pyodide-build is a submodule and we do not directly modify the source code in this repository. All the pyodide-build-related changes should'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Refer to `docs/development/debugging.md` for tips on debugging, including how to handle linker errors and build with symbols.' in text, "expected to find: " + '- Refer to `docs/development/debugging.md` for tips on debugging, including how to handle linker errors and build with symbols.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Python:** Improve the Python interpreter, including standard library compatibility, performance, and size.' in text, "expected to find: " + '- **Python:** Improve the Python interpreter, including standard library compatibility, performance, and size.'[:80]

