"""Behavioral checks for luisacompute-set-up-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/luisacompute")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The project is described in the SIGGRAPH Asia 2022 paper *"LuisaRender: A High-Performance Rendering Framework with Layered and Unified Interfaces on Stream Architectures"*.' in text, "expected to find: " + 'The project is described in the SIGGRAPH Asia 2022 paper *"LuisaRender: A High-Performance Rendering Framework with Layered and Unified Interfaces on Stream Architectures"*.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'LuisaCompute is a high-performance cross-platform computing framework for graphics and beyond. It provides:' in text, "expected to find: " + 'LuisaCompute is a high-performance cross-platform computing framework for graphics and beyond. It provides:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- A unified runtime with resource wrappers for cross-platform resource management and command scheduling' in text, "expected to find: " + '- A unified runtime with resource wrappers for cross-platform resource management and command scheduling'[:80]

