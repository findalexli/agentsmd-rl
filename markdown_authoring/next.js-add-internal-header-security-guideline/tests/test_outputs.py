"""Behavioral checks for next.js-add-internal-header-security-guideline (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/next.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**When reviewing PRs: if new code reads a request header that is not a standard HTTP header (like `content-type`, `accept`, `user-agent`, `host`, `authorization`, `cookie`, etc.), flag it for security' in text, "expected to find: " + '**When reviewing PRs: if new code reads a request header that is not a standard HTTP header (like `content-type`, `accept`, `user-agent`, `host`, `authorization`, `cookie`, etc.), flag it for security'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Next.js strips internal headers from incoming requests via `filterInternalHeaders()` in `packages/next/src/server/lib/server-ipc/utils.ts`. This runs at the entry point in `packages/next/src/server/li' in text, "expected to find: " + 'Next.js strips internal headers from incoming requests via `filterInternalHeaders()` in `packages/next/src/server/lib/server-ipc/utils.ts`. This runs at the entry point in `packages/next/src/server/li'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '### Server Security: Internal Header Filtering' in text, "expected to find: " + '### Server Security: Internal Header Filtering'[:80]

