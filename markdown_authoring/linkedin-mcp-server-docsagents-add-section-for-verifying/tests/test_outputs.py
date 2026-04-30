"""Behavioral checks for linkedin-mcp-server-docsagents-add-section-for-verifying (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/linkedin-mcp-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Always verify scraping bugs end-to-end against live LinkedIn, not just code analysis. Assume a valid login profile already exists at `~/.linkedin-mcp/profile/`. Start the server with HTTP transport in' in text, "expected to find: " + 'Always verify scraping bugs end-to-end against live LinkedIn, not just code analysis. Assume a valid login profile already exists at `~/.linkedin-mcp/profile/`. Start the server with HTTP transport in'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-d \'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_person_profile","arguments":{"linkedin_username":"williamhgates","sections":"posts"}}}\'' in text, "expected to find: " + '-d \'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_person_profile","arguments":{"linkedin_username":"williamhgates","sections":"posts"}}}\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-d \'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\'' in text, "expected to find: " + '-d \'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}\''[:80]

