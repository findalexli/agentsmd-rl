"""Behavioral checks for memmachine-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/memmachine")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.MD')
    assert 'This guide helps AI coding assistants (like Cursor, Claude Code, Codex, etc.) understand how to help developers integrate MemMachine into their applications. MemMachine is an open-source memory layer ' in text, "expected to find: " + 'This guide helps AI coding assistants (like Cursor, Claude Code, Codex, etc.) understand how to help developers integrate MemMachine into their applications. MemMachine is an open-source memory layer '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.MD')
    assert '3. **Use appropriate roles**: In the Python SDK, `role` defaults to `"user"`. Use `role="user"` for user messages, `role="assistant"` for AI responses, and `role="system"` for system messages. Note: I' in text, "expected to find: " + '3. **Use appropriate roles**: In the Python SDK, `role` defaults to `"user"`. Use `role="user"` for user messages, `role="assistant"` for AI responses, and `role="system"` for system messages. Note: I'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.MD')
    assert 'Search for memories across episodic and semantic memory. Required fields: `org_id`, `project_id`, `query`. Optional fields: `top_k` (defaults to `10`), `filter` (defaults to `""`), `types` (defaults t' in text, "expected to find: " + 'Search for memories across episodic and semantic memory. Required fields: `org_id`, `project_id`, `query`. Optional fields: `top_k` (defaults to `10`), `filter` (defaults to `""`), `types` (defaults t'[:80]

