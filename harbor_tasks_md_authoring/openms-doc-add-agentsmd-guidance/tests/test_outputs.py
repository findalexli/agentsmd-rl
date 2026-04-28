"""Behavioral checks for openms-doc-add-agentsmd-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openms")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Doxygen (if built) in `OpenMS-build/doc/html/` including `index.html`, `developer_coding_conventions.html`, `developer_cpp_guide.html`, `developer_how_to_write_tests.html`, `howto_commit_messages.ht' in text, "expected to find: " + '- Doxygen (if built) in `OpenMS-build/doc/html/` including `index.html`, `developer_coding_conventions.html`, `developer_cpp_guide.html`, `developer_how_to_write_tests.html`, `howto_commit_messages.ht'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Gotchas: autowrap returns Python strings; do not `.decode()`. Avoid `cdef` for autowrap string returns. Avoid `cdef` typed variables for autowrap return values inside `def` methods; use Python type ' in text, "expected to find: " + '- Gotchas: autowrap returns Python strings; do not `.decode()`. Avoid `cdef` for autowrap string returns. Avoid `cdef` typed variables for autowrap return values inside `def` methods; use Python type '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file summarizes repo-specific conventions and workflows for contributors and automated changes. It is intentionally concise; use the linked docs for full details.' in text, "expected to find: " + 'This file summarizes repo-specific conventions and workflows for contributors and automated changes. It is intentionally concise; use the linked docs for full details.'[:80]

