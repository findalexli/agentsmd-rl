"""Behavioral checks for antigravity-awesome-skills-add-skill-moyu (markdown_authoring task).

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
    text = _read('skills/moyu/SKILL.md')
    assert "You are a Staff engineer who deeply understands that less is more. Throughout your career, you've seen too many projects fail because of over-engineering. Your proudest PR was a 3-line diff that fixed" in text, "expected to find: " + "You are a Staff engineer who deeply understands that less is more. Throughout your career, you've seen too many projects fail because of over-engineering. Your proudest PR was a 3-line diff that fixed"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/moyu/SKILL.md')
    assert "When the user explicitly asks, go ahead and deliver fully. Moyu's core principle is **don't do what wasn't asked for**, not **refuse to do what was asked for**." in text, "expected to find: " + "When the user explicitly asks, go ahead and deliver fully. Moyu's core principle is **don't do what wasn't asked for**, not **refuse to do what was asked for**."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/moyu/SKILL.md')
    assert '| One implementation with interface + factory + strategy | Write the implementation directly — no interface needed without a second implementation |' in text, "expected to find: " + '| One implementation with interface + factory + strategy | Write the implementation directly — no interface needed without a second implementation |'[:80]

