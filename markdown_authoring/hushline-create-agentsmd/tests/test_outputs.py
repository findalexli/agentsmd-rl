"""Behavioral checks for hushline-create-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hushline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "This file provides operating guidance for coding agents working in the Hush Line repository. We are a 501(c)(3) non-profit based in the United States, and this software is critical for our users' oper" in text, "expected to find: " + "This file provides operating guidance for coding agents working in the Hush Line repository. We are a 501(c)(3) non-profit based in the United States, and this software is critical for our users' oper"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Message recipients: journalists and newsrooms, legal teams, employers and boards, educators and administrators, organizers and activists, software developers.' in text, "expected to find: " + '- Message recipients: journalists and newsrooms, legal teams, employers and boards, educators and administrators, organizers and activists, software developers.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For notification/email changes, validate all three modes: generic notification only, include message content, encrypt entire email body.' in text, "expected to find: " + '- For notification/email changes, validate all three modes: generic notification only, include message content, encrypt entire email body.'[:80]

