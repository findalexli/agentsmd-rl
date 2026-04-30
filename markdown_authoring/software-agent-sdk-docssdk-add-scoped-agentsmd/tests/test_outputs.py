"""Behavioral checks for software-agent-sdk-docssdk-add-scoped-agentsmd (markdown_authoring task).

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
    text = _read('openhands-sdk/openhands/sdk/AGENTS.md')
    assert '- Add/adjust unit tests under `tests/sdk/` mirroring the SDK path (for example, changes to `openhands-sdk/openhands/sdk/tool/tool.py` should be covered in `tests/sdk/tool/test_tool.py`).' in text, "expected to find: " + '- Add/adjust unit tests under `tests/sdk/` mirroring the SDK path (for example, changes to `openhands-sdk/openhands/sdk/tool/tool.py` should be covered in `tests/sdk/tool/test_tool.py`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-sdk/openhands/sdk/AGENTS.md')
    assert '- Keep new modules within the closest existing subpackage (e.g., `llm/`, `tool/`, `event/`, `agent/`) and follow local naming patterns.' in text, "expected to find: " + '- Keep new modules within the closest existing subpackage (e.g., `llm/`, `tool/`, `event/`, `agent/`) and follow local naming patterns.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-sdk/openhands/sdk/AGENTS.md')
    assert '- When changing Pydantic models or serialized event shapes, preserve backward compatibility so older persisted data can still load.' in text, "expected to find: " + '- When changing Pydantic models or serialized event shapes, preserve backward compatibility so older persisted data can still load.'[:80]

