"""Behavioral checks for webmcp-tools-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/webmcp-tools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Step                     | Agent Action                                                                          | Expected Behavior                                                                  ' in text, "expected to find: " + '| Step                     | Agent Action                                                                          | Expected Behavior                                                                  '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **Invocation**           | The agent calls the tool by its registered name (using the `toolname` attribute).     | The browser automatically brings the associated form into focus and populates its f' in text, "expected to find: " + '| **Invocation**           | The agent calls the tool by its registered name (using the `toolname` attribute).     | The browser automatically brings the associated form into focus and populates its f'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| **Submission (Default)** | The agent waits for user input.                                                       | By default, the form remains visible, and the user must manually click the **Submit' in text, "expected to find: " + '| **Submission (Default)** | The agent waits for user input.                                                       | By default, the form remains visible, and the user must manually click the **Submit'[:80]

