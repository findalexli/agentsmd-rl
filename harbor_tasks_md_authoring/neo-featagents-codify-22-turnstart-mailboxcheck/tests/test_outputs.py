"""Behavioral checks for neo-featagents-codify-22-turnstart-mailboxcheck (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **PR #10379** (Shape B Webhook Delivery, 2026-04-26): `WebhookDeliveryService.mjs` was authored with `constructor({databaseService, logger})` instead of the canonical `class X extends Base { static ' in text, "expected to find: " + '- **PR #10379** (Shape B Webhook Delivery, 2026-04-26): `WebhookDeliveryService.mjs` was authored with `constructor({databaseService, logger})` instead of the canonical `class X extends Base { static '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The skill table above governs **multi-step lifecycle discipline** (ticket creation, PR cycle, review cycle). The two sections below — §22 (turn-start mailbox check) and §23 (authoring-time sibling-fil' in text, "expected to find: " + 'The skill table above governs **multi-step lifecycle discipline** (ticket creation, PR cycle, review cycle). The two sections below — §22 (turn-start mailbox check) and §23 (authoring-time sibling-fil'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **PR #10381** (Shape C bridge daemon, merged 2026-04-26): `bridge-daemon.mjs` correctly used raw `better-sqlite3` + `json_extract` queries because the `ai/scripts/` convention is "out-of-process pol' in text, "expected to find: " + '- **PR #10381** (Shape C bridge daemon, merged 2026-04-26): `bridge-daemon.mjs` correctly used raw `better-sqlite3` + `json_extract` queries because the `ai/scripts/` convention is "out-of-process pol'[:80]

