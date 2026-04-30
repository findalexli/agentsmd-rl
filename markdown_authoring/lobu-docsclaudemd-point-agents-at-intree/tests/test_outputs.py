"""Behavioral checks for lobu-docsclaudemd-point-agents-at-intree (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lobu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The live Owletto MCP server, ClientSDK, sandbox, and tool registry are in `packages/owletto-backend/` of this repo. The prod `summaries-app-owletto-app` image is built from there (`docker/app/Dockerfi' in text, "expected to find: " + 'The live Owletto MCP server, ClientSDK, sandbox, and tool registry are in `packages/owletto-backend/` of this repo. The prod `summaries-app-owletto-app` image is built from there (`docker/app/Dockerfi'[:80]

