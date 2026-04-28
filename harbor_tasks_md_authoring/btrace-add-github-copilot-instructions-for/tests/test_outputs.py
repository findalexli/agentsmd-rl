"""Behavioral checks for btrace-add-github-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/btrace")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'BTrace is a safe, dynamic tracing tool for the Java platform. It dynamically instruments running Java applications to inject tracing code at runtime using bytecode instrumentation.' in text, "expected to find: " + 'BTrace is a safe, dynamic tracing tool for the Java platform. It dynamically instruments running Java applications to inject tracing code at runtime using bytecode instrumentation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Commit style**: Conventional Commits (e.g., `feat(core): add probe`, `fix(instr): handle null arg`)' in text, "expected to find: " + '- **Commit style**: Conventional Commits (e.g., `feat(core): add probe`, `fix(instr): handle null arg`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Core modules**: `btrace-core`, `btrace-agent`, `btrace-runtime`, `btrace-client`, `btrace-instr`' in text, "expected to find: " + '- **Core modules**: `btrace-core`, `btrace-agent`, `btrace-runtime`, `btrace-client`, `btrace-instr`'[:80]

