"""Behavioral checks for software-agent-sdk-docs-align-agentsmd-guidance-across (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert '- This is a `uv`-managed Python monorepo (single `uv.lock` at repo root) with multiple distributable packages: `openhands-sdk/` (SDK), `openhands-tools/` (built-in tools), `openhands-workspace/` (work' in text, "expected to find: " + '- This is a `uv`-managed Python monorepo (single `uv.lock` at repo root) with multiple distributable packages: `openhands-sdk/` (SDK), `openhands-tools/` (built-in tools), `openhands-workspace/` (work'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Put unit tests under the corresponding domain folder in `tests/` (e.g., `tests/sdk`, `tests/tools`, `tests/workspace`). For example, changes to `openhands-sdk/openhands/sdk/tool/tool.py` should be c' in text, "expected to find: " + '- Put unit tests under the corresponding domain folder in `tests/` (e.g., `tests/sdk`, `tests/tools`, `tests/workspace`). For example, changes to `openhands-sdk/openhands/sdk/tool/tool.py` should be c'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `examples/` contains runnable patterns; `tests/` is split by domain (`tests/sdk`, `tests/tools`, `tests/workspace`, `tests/agent_server`, etc.).' in text, "expected to find: " + '- `examples/` contains runnable patterns; `tests/` is split by domain (`tests/sdk`, `tests/tools`, `tests/workspace`, `tests/agent_server`, etc.).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-sdk/openhands/sdk/AGENTS.md')
    assert '## Package Structure & Module Organization' in text, "expected to find: " + '## Package Structure & Module Organization'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-sdk/openhands/sdk/AGENTS.md')
    assert '# Package Guidelines' in text, "expected to find: " + '# Package Guidelines'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-tools/openhands/tools/AGENTS.md')
    assert '## Package Structure & Module Organization' in text, "expected to find: " + '## Package Structure & Module Organization'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-tools/openhands/tools/AGENTS.md')
    assert '# Package Guidelines' in text, "expected to find: " + '# Package Guidelines'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-workspace/openhands/workspace/AGENTS.md')
    assert '## Package Structure & Module Organization' in text, "expected to find: " + '## Package Structure & Module Organization'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('openhands-workspace/openhands/workspace/AGENTS.md')
    assert '# Package Guidelines' in text, "expected to find: " + '# Package Guidelines'[:80]

