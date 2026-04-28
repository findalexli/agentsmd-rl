"""Behavioral checks for neo-docspullrequest-mandate-a2a-notification-for (markdown_authoring task).

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
    text = _read('.agent/skills/pull-request/references/pull-request-workflow.md')
    assert 'If you are operating inside the canonical `neomjs/neo` repository as a core swarm member (e.g., `@neo-opus-4-7`, `@neo-gemini-3-1-pro`), immediately after successfully opening a PR, you MUST send an A' in text, "expected to find: " + 'If you are operating inside the canonical `neomjs/neo` repository as a core swarm member (e.g., `@neo-opus-4-7`, `@neo-gemini-3-1-pro`), immediately after successfully opening a PR, you MUST send an A'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pull-request/references/pull-request-workflow.md')
    assert 'This strict feedback loop prevents duplicated work and confusion over ticket ownership when multiple agents are running concurrently. This rule strictly applies only to the `neomjs/neo` repo for the c' in text, "expected to find: " + 'This strict feedback loop prevents duplicated work and confusion over ticket ownership when multiple agents are running concurrently. This rule strictly applies only to the `neomjs/neo` repo for the c'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/pull-request/references/pull-request-workflow.md')
    assert '### 6.2 The Core Swarm A2A Notification Mandate' in text, "expected to find: " + '### 6.2 The Core Swarm A2A Notification Mandate'[:80]

