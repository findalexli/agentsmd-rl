"""Behavioral checks for software-agent-sdk-docs-add-packagescoped-agentsmd-guides (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/software-agent-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-tools/openhands/tools/AGENTS.md')
    assert '- Tool names, parameter schemas, and output schemas are user-facing and often referenced in tests like `tests/tools/test_tool_name_consistency.py`; avoid breaking changes. If a schema must change, pro' in text, "expected to find: " + '- Tool names, parameter schemas, and output schemas are user-facing and often referenced in tests like `tests/tools/test_tool_name_consistency.py`; avoid breaking changes. If a schema must change, pro'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-tools/openhands/tools/AGENTS.md')
    assert '- When adding runtime-loaded assets (Jinja `.j2` templates or JS under `browser_use/js/`), ensure they are included as package data (and update the agent-server PyInstaller spec when needed).' in text, "expected to find: " + '- When adding runtime-loaded assets (Jinja `.j2` templates or JS under `browser_use/js/`), ensure they are included as package data (and update the agent-server PyInstaller spec when needed).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-tools/openhands/tools/AGENTS.md')
    assert '- Prefer real code paths over mocks; when mocking is unavoidable (e.g. external processes), centralize setup in `tests/conftest.py` or `tests/tools/<tool>/conftest.py`.' in text, "expected to find: " + '- Prefer real code paths over mocks; when mocking is unavoidable (e.g. external processes), centralize setup in `tests/conftest.py` or `tests/tools/<tool>/conftest.py`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-workspace/openhands/workspace/AGENTS.md')
    assert '- The published import surface is `openhands-workspace/openhands/workspace/__init__.py` (`__all__` is treated as public API). Keep imports lightweight so `import openhands.workspace` does not pull in ' in text, "expected to find: " + '- The published import surface is `openhands-workspace/openhands/workspace/__init__.py` (`__all__` is treated as public API). Keep imports lightweight so `import openhands.workspace` does not pull in '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-workspace/openhands/workspace/AGENTS.md')
    assert '- Tests live under `tests/workspace/` and generally validate import behavior, model fields, and command invocation. Prefer patching command executors instead of requiring real Docker in unit tests.' in text, "expected to find: " + '- Tests live under `tests/workspace/` and generally validate import behavior, model fields, and command invocation. Prefer patching command executors instead of requiring real Docker in unit tests.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-workspace/openhands/workspace/AGENTS.md')
    assert '- This directory (`openhands-workspace/openhands/workspace/`) contains workspace implementations under the `openhands.workspace.*` namespace (Docker, Apptainer, cloud, and API-remote).' in text, "expected to find: " + '- This directory (`openhands-workspace/openhands/workspace/`) contains workspace implementations under the `openhands.workspace.*` namespace (Docker, Apptainer, cloud, and API-remote).'[:80]

