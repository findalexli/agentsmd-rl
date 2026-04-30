"""Behavioral checks for everclaw-community-branches-add-agent-integration-section-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everclaw-community-branches")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'The proxy (port 8083) auto-opens blockchain sessions, auto-renews before expiry, and injects all required auth headers. The bash scripts (`session.sh`, `chat.sh`) are available for manual debugging bu' in text, "expected to find: " + 'The proxy (port 8083) auto-opens blockchain sessions, auto-renews before expiry, and injects all required auth headers. The bash scripts (`session.sh`, `chat.sh`) are available for manual debugging bu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**If you are an AI agent (OpenClaw, Claude, etc.), use the OpenAI-compatible proxy for all Morpheus inference. Do NOT use the bash scripts (session.sh, chat.sh) -- the proxy handles sessions, auth, an' in text, "expected to find: " + '**If you are an AI agent (OpenClaw, Claude, etc.), use the OpenAI-compatible proxy for all Morpheus inference. Do NOT use the bash scripts (session.sh, chat.sh) -- the proxy handles sessions, auth, an'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '-d \'{"model": "kimi-k2.5", "messages": [{"role": "user", "content": "Hello"}], "stream": false}\'' in text, "expected to find: " + '-d \'{"model": "kimi-k2.5", "messages": [{"role": "user", "content": "Hello"}], "stream": false}\''[:80]

