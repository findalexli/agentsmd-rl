"""Behavioral checks for selenium-py-add-in-rules-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/selenium")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert 'Run tests via `bazel test //py:test-{browser}` or `bazel test //py:test-{browser}-bidi`, where `{browser}` is the target browser (e.g., `chrome`, `firefox`, `edge`). See `/AGENTS.md` for toolchain det' in text, "expected to find: " + 'Run tests via `bazel test //py:test-{browser}` or `bazel test //py:test-{browser}-bidi`, where `{browser}` is the target browser (e.g., `chrome`, `firefox`, `edge`). See `/AGENTS.md` for toolchain det'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert 'For testing: use `bazel test //py/...` which employs a hermetic Python 3.10+ toolchain (see `/AGENTS.md`).' in text, "expected to find: " + 'For testing: use `bazel test //py/...` which employs a hermetic Python 3.10+ toolchain (see `/AGENTS.md`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('py/AGENTS.md')
    assert 'See the **Type hints** section for guidance on preferred type annotation syntax (including unions).' in text, "expected to find: " + 'See the **Type hints** section for guidance on preferred type annotation syntax (including unions).'[:80]

