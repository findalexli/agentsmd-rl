"""Behavioral checks for brush-docs-add-an-initial-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/brush")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Compatibility tests**: For any compatibility-related fixes, it's critical to add new test cases to the compat tests (see docs/how-to/run-tests.md and section 3 for when breaking changes apply)" in text, "expected to find: " + "- **Compatibility tests**: For any compatibility-related fixes, it's critical to add new test cases to the compat tests (see docs/how-to/run-tests.md and section 3 for when breaking changes apply)"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Categories are defined in `trace_categories.rs` modules (e.g., `COMMANDS`, `COMPLETION`, `EXPANSION`, `FUNCTIONS`, `INPUT`, `JOBS`, `PARSE`, `PATTERN`, `UNIMPLEMENTED`)' in text, "expected to find: " + '- Categories are defined in `trace_categories.rs` modules (e.g., `COMMANDS`, `COMPLETION`, `EXPANSION`, `FUNCTIONS`, `INPUT`, `JOBS`, `PARSE`, `PATTERN`, `UNIMPLEMENTED`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow good software engineering practice: start by validating the specific area being changed, then iteratively move to incrementally broader sets of tests' in text, "expected to find: " + '- Follow good software engineering practice: start by validating the specific area being changed, then iteratively move to incrementally broader sets of tests'[:80]

