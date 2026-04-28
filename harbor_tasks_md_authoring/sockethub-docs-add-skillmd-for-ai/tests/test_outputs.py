"""Behavioral checks for sockethub-docs-add-skillmd-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sockethub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'description: Bridges web applications to messaging protocols (IRC, XMPP, RSS/Atom) via ActivityStreams. Use when building chat clients, connecting to IRC channels, sending XMPP messages, fetching RSS ' in text, "expected to find: " + 'description: Bridges web applications to messaging protocols (IRC, XMPP, RSS/Atom) via ActivityStreams. Use when building chat clients, connecting to IRC channels, sending XMPP messages, fetching RSS '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'A polyglot messaging gateway that translates ActivityStreams messages to protocol-specific formats, enabling browser JavaScript to communicate with IRC, XMPP, and feed services.' in text, "expected to find: " + 'A polyglot messaging gateway that translates ActivityStreams messages to protocol-specific formats, enabling browser JavaScript to communicate with IRC, XMPP, and feed services.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '| XMPP | `xmpp` | connect, join, leave, send, update, request-friend, make-friend, remove-friend, query, disconnect |' in text, "expected to find: " + '| XMPP | `xmpp` | connect, join, leave, send, update, request-friend, make-friend, remove-friend, query, disconnect |'[:80]

