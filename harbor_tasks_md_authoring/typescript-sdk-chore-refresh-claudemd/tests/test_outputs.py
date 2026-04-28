"""Behavioral checks for typescript-sdk-chore-refresh-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/typescript-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **Protocol Layer** (`src/shared/protocol.ts`) - The abstract `Protocol` class that handles JSON-RPC message routing, request/response correlation, capability negotiation, and transport management. ' in text, "expected to find: " + '2. **Protocol Layer** (`src/shared/protocol.ts`) - The abstract `Protocol` class that handles JSON-RPC message routing, request/response correlation, capability negotiation, and transport management. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Types Layer** (`src/types.ts`) - Protocol types generated from the MCP specification. All JSON-RPC message types, schemas, and protocol constants are defined here using Zod v4.' in text, "expected to find: " + '1. **Types Layer** (`src/types.ts`) - Protocol types generated from the MCP specification. All JSON-RPC message types, schemas, and protocol constants are defined here using Zod v4.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Streamable HTTP** (`src/server/streamableHttp.ts`, `src/client/streamableHttp.ts`) - Recommended transport for remote servers, supports SSE for streaming' in text, "expected to find: " + '- **Streamable HTTP** (`src/server/streamableHttp.ts`, `src/client/streamableHttp.ts`) - Recommended transport for remote servers, supports SSE for streaming'[:80]

