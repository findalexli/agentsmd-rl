"""Behavioral checks for go-sdk-chore-configure-a-simple-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/go-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-bug/SKILLS.md')
    assert "3.  Create an implementation plan that describes how you intend to fix the bug. Don't proceed without approval." in text, "expected to find: " + "3.  Create an implementation plan that describes how you intend to fix the bug. Don't proceed without approval."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-bug/SKILLS.md')
    assert '5.  Verify the fix with the test case and run all tests to ensure no regressions.' in text, "expected to find: " + '5.  Verify the fix with the test case and run all tests to ensure no regressions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/fix-bug/SKILLS.md')
    assert 'description: Confirm, debug and fix bugs reported via GitHub issues.' in text, "expected to find: " + 'description: Confirm, debug and fix bugs reported via GitHub issues.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   `mcp`: The core package defining the primary APIs for constructing and using MCP clients and servers. This is where most logic resides.' in text, "expected to find: " + '-   `mcp`: The core package defining the primary APIs for constructing and using MCP clients and servers. This is where most logic resides.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   **Conformance Tests**: Use the following scripts to run the official MCP conformance tests against the SDK.' in text, "expected to find: " + '-   **Conformance Tests**: Use the following scripts to run the official MCP conformance tests against the SDK.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   **README.md**: Do NOT edit `README.md` directly. It is generated from `internal/readme/README.src.md`.' in text, "expected to find: " + '-   **README.md**: Do NOT edit `README.md` directly. It is generated from `internal/readme/README.src.md`.'[:80]

