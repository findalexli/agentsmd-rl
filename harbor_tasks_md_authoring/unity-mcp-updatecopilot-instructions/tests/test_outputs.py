"""Behavioral checks for unity-mcp-updatecopilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unity-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Unity-Tests**: [Unity-Tests/](Unity-Tests/) contains projects for different Unity versions (2022, 2023, 6000) linking locally to the Plugin.' in text, "expected to find: " + '- **Unity-Tests**: [Unity-Tests/](Unity-Tests/) contains projects for different Unity versions (2022, 2023, 6000) linking locally to the Plugin.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **C#**: Use 4 spaces indentation. PascalCase for classes/methods/properties, `_camelCase` for private readonly fields.' in text, "expected to find: " + '- **C#**: Use 4 spaces indentation. PascalCase for classes/methods/properties, `_camelCase` for private readonly fields.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **MCP Tools**: Implemented using attributes in the Plugin. Reflection-based access via `ReflectorNet`.' in text, "expected to find: " + '- **MCP Tools**: Implemented using attributes in the Plugin. Reflection-based access via `ReflectorNet`.'[:80]

