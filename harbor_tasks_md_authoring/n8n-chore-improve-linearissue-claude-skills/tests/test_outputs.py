"""Behavioral checks for n8n-chore-improve-linearissue-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/n8n")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/plugins/n8n/skills/linear-issue/SKILL.md')
    assert '> One or more of your remotes point to the **public** `n8n-io/n8n` repo. Mixed remotes are not allowed — you must work in a **separate local clone** of `n8n-io/n8n-private` with no references to the p' in text, "expected to find: " + '> One or more of your remotes point to the **public** `n8n-io/n8n` repo. Mixed remotes are not allowed — you must work in a **separate local clone** of `n8n-io/n8n-private` with no references to the p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/plugins/n8n/skills/linear-issue/SKILL.md')
    assert '> For the full process, see: https://www.notion.so/n8n/Processing-critical-high-security-bugs-vulnerabilities-in-private-2f45b6e0c94f803da806f472111fb1a5' in text, "expected to find: " + '> For the full process, see: https://www.notion.so/n8n/Processing-critical-high-security-bugs-vulnerabilities-in-private-2f45b6e0c94f803da806f472111fb1a5'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/plugins/n8n/skills/linear-issue/SKILL.md')
    assert 'b. If **any** remote URL contains `n8n-io/n8n` without the `-private` suffix (i.e. matches the public repo), **stop immediately** and tell the user:' in text, "expected to find: " + 'b. If **any** remote URL contains `n8n-io/n8n` without the `-private` suffix (i.e. matches the public repo), **stop immediately** and tell the user:'[:80]

