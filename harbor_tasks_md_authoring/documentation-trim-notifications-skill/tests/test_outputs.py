"""Behavioral checks for documentation-trim-notifications-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/documentation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md')
    assert 'description: Use when adding or reviewing live-trading `Notify.*` calls (Email, SMS, Telegram, Web/Webhook, FTP/SFTP) in a QuantConnect/LEAN algorithm. Notifications run in QuantConnect Cloud live tra' in text, "expected to find: " + 'description: Use when adding or reviewing live-trading `Notify.*` calls (Email, SMS, Telegram, Web/Webhook, FTP/SFTP) in a QuantConnect/LEAN algorithm. Notifications run in QuantConnect Cloud live tra'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md')
    assert '**Telegram.** `id` is the **group ID** as it appears in the Telegram web URL — a negative integer like `-503016366`. The `token` argument is optional **only** if `@quantconnect_notifications_bot` has ' in text, "expected to find: " + '**Telegram.** `id` is the **group ID** as it appears in the Telegram web URL — a negative integer like `-503016366`. The `token` argument is optional **only** if `@quantconnect_notifications_bot` has '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('03 Writing Algorithms/40 Live Trading/40 Notifications/SKILL.md')
    assert '**Webhook.** HTTP POST with a 300 s response timeout — endpoints that block on synchronous expensive work silently time out, and there is no built-in retry. Discord webhooks expect a JSON body keyed o' in text, "expected to find: " + '**Webhook.** HTTP POST with a 300 s response timeout — endpoints that block on synchronous expensive work silently time out, and there is no built-in retry. Discord webhooks expect a JSON body keyed o'[:80]

