"""Behavioral checks for hermes-webui-revert-agentsmd-rewrite (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-webui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Claude-style web UI for Hermes. Chat, workspace file browser, cron/skills/memory viewers.' in text, "expected to find: " + '- Claude-style web UI for Hermes. Chat, workspace file browser, cron/skills/memory viewers.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'whichever workspace the user has selected in the UI at the moment they sent that message.' in text, "expected to find: " + 'whichever workspace the user has selected in the UI at the moment they sent that message.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When running as an agent invoked from the web UI, each user message is prefixed with:' in text, "expected to find: " + 'When running as an agent invoked from the web UI, each user message is prefixed with:'[:80]

