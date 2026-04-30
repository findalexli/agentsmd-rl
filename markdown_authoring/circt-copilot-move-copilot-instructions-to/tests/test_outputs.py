"""Behavioral checks for circt-copilot-move-copilot-instructions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/circt")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always run `clang-format` on C++ code changes and `yapf` on Python code changes.' in text, "expected to find: " + '- Always run `clang-format` on C++ code changes and `yapf` on Python code changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('lib/Dialect/ESI/runtime/AGENTS.md')
    assert 'The GTest-based unit tests live in `lib/Dialect/ESI/runtime/tests/cpp` and they are built with the ESIRuntimeCppTests target. They can be run independently or they are run by pytest if the binary is p' in text, "expected to find: " + 'The GTest-based unit tests live in `lib/Dialect/ESI/runtime/tests/cpp` and they are built with the ESIRuntimeCppTests target. They can be run independently or they are run by pytest if the binary is p'[:80]

