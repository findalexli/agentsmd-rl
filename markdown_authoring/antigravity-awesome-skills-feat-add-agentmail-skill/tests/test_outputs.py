"""Behavioral checks for antigravity-awesome-skills-feat-add-agentmail-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentmail/SKILL.md')
    assert 'description: Use when an AI agent needs email capabilities — creating email accounts, sending/receiving email, managing webhooks, or checking karma balance. Triggers on requests like "send an email", ' in text, "expected to find: " + 'description: Use when an AI agent needs email capabilities — creating email accounts, sending/receiving email, managing webhooks, or checking karma balance. Triggers on requests like "send an email", '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentmail/SKILL.md')
    assert 'AgentMail gives AI agents real email addresses (`@theagentmail.net`) with a REST API. Agents can send and receive email, sign up for services (GitHub, AWS, Slack, etc.), and get verification codes. A ' in text, "expected to find: " + 'AgentMail gives AI agents real email addresses (`@theagentmail.net`) with a REST API. Agents can send and receive email, sign up for services (GitHub, AWS, Slack, etc.), and get verification codes. A '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agentmail/SKILL.md')
    assert 'type MessageDetail = Message & { cc: string[] | null; bcc: string[] | null; bodyText: string | null; bodyHtml: string | null; inReplyTo: string | null; references: string | null; attachments: Attachme' in text, "expected to find: " + 'type MessageDetail = Message & { cc: string[] | null; bcc: string[] | null; bodyText: string | null; bodyHtml: string | null; inReplyTo: string | null; references: string | null; attachments: Attachme'[:80]

