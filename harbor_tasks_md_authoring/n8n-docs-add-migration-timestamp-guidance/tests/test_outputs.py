"""Behavioral checks for n8n-docs-add-migration-timestamp-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/n8n")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/@n8n/db/AGENTS.md')
    assert 'must be the **exact** Unix millisecond timestamp at the time of creation — do' in text, "expected to find: " + 'must be the **exact** Unix millisecond timestamp at the time of creation — do'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/@n8n/db/AGENTS.md')
    assert 'Migration files are named `{TIMESTAMP}-{DescriptiveName}.ts`. The timestamp' in text, "expected to find: " + 'Migration files are named `{TIMESTAMP}-{DescriptiveName}.ts`. The timestamp'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/@n8n/db/AGENTS.md')
    assert 'not round or fabricate a value. Use `Date.now()` in a Node REPL or' in text, "expected to find: " + 'not round or fabricate a value. Use `Date.now()` in a Node REPL or'[:80]

