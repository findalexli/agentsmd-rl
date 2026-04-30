"""Behavioral checks for sdk-typescript-docs-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sdk-typescript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`strands-py/strands/`**: Python package source with agent, models, multiagent, session, tools, and type modules' in text, "expected to find: " + '- **`strands-py/strands/`**: Python package source with agent, models, multiagent, session, tools, and type modules'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`wit/`**: WebAssembly Interface Type (WIT) definitions defining the contract between the TS SDK and WASM hosts' in text, "expected to find: " + '- **`wit/`**: WebAssembly Interface Type (WIT) definitions defining the contract between the TS SDK and WASM hosts'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`docs/`**: Project documentation (testing guidelines, dependency management, PR guidelines)' in text, "expected to find: " + '- **`docs/`**: Project documentation (testing guidelines, dependency management, PR guidelines)'[:80]

