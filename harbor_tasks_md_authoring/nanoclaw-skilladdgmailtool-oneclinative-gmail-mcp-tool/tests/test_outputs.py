"""Behavioral checks for nanoclaw-skilladdgmailtool-oneclinative-gmail-mcp-tool (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail-tool/SKILL.md')
    assert '**Why the `zod-to-json-schema` pin:** `@gongrzhe/server-gmail-autoauth-mcp@1.1.11` has loose deps (`zod-to-json-schema: ^3.22.1`, `zod: ^3.22.4`). pnpm resolves `zod-to-json-schema` to the latest 3.25' in text, "expected to find: " + '**Why the `zod-to-json-schema` pin:** `@gongrzhe/server-gmail-autoauth-mcp@1.1.11` has loose deps (`zod-to-json-schema: ^3.22.1`, `zod: ^3.22.4`). pnpm resolves `zod-to-json-schema` to the latest 3.25'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail-tool/SKILL.md')
    assert '- **Stub format is OneCLI-prescribed.** The `access_token: "onecli-managed"` pattern with `expiry_date: 99999999999999` tells the Google auth client the token is valid; OneCLI intercepts the outgoing ' in text, "expected to find: " + '- **Stub format is OneCLI-prescribed.** The `access_token: "onecli-managed"` pattern with `expiry_date: 99999999999999` tells the Google auth client the token is valid; OneCLI intercepts the outgoing '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-gmail-tool/SKILL.md')
    assert 'Tools exposed (from `gmail-mcp@1.1.11`, surfaced to the agent as `mcp__gmail__<name>`): `search_emails`, `read_email`, `send_email`, `draft_email`, `delete_email`, `modify_email`, `batch_modify_emails' in text, "expected to find: " + 'Tools exposed (from `gmail-mcp@1.1.11`, surfaced to the agent as `mcp__gmail__<name>`): `search_emails`, `read_email`, `send_email`, `draft_email`, `delete_email`, `modify_email`, `batch_modify_emails'[:80]

