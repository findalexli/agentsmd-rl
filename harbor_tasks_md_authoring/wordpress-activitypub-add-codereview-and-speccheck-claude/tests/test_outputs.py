"""Behavioral checks for wordpress-activitypub-add-codereview-and-speccheck-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wordpress-activitypub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-review.md')
    assert 'description: Review code changes for quality, WordPress coding standards, and ActivityPub conventions. Use when asked to review a PR, branch, diff, or specific files.' in text, "expected to find: " + 'description: Review code changes for quality, WordPress coding standards, and ActivityPub conventions. Use when asked to review a PR, branch, diff, or specific files.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-review.md')
    assert 'You are a code reviewer for the WordPress ActivityPub plugin. Review changes thoroughly and provide actionable feedback.' in text, "expected to find: " + 'You are a code reviewer for the WordPress ActivityPub plugin. Review changes thoroughly and provide actionable feedback.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-review.md')
    assert "- Don't nitpick formatting that PHPCS would catch — focus on logic, architecture, and security." in text, "expected to find: " + "- Don't nitpick formatting that PHPCS would catch — focus on logic, architecture, and security."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/spec-check.md')
    assert 'You are an ActivityPub spec compliance auditor for the WordPress ActivityPub plugin. You check endpoint implementations against the W3C ActivityPub spec and the SWICG ActivityPub API task force requir' in text, "expected to find: " + 'You are an ActivityPub spec compliance auditor for the WordPress ActivityPub plugin. You check endpoint implementations against the W3C ActivityPub spec and the SWICG ActivityPub API task force requir'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/spec-check.md')
    assert 'description: Check ActivityPub endpoints against the W3C ActivityPub spec and SWICG ActivityPub API spec. Use when asked to check spec compliance, verify endpoints, or audit federation conformance.' in text, "expected to find: " + 'description: Check ActivityPub endpoints against the W3C ActivityPub spec and SWICG ActivityPub API spec. Use when asked to check spec compliance, verify endpoints, or audit federation conformance.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/spec-check.md')
    assert '- **SWICG ActivityPub API** — https://github.com/swicg/activitypub-api (emerging requirements for OAuth, SSE, discovery, collections)' in text, "expected to find: " + '- **SWICG ActivityPub API** — https://github.com/swicg/activitypub-api (emerging requirements for OAuth, SSE, discovery, collections)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr/SKILL.md')
    assert 'Before creating a PR, delegate to the **code-review** agent to review all changes on the branch. Address any critical issues before proceeding.' in text, "expected to find: " + 'Before creating a PR, delegate to the **code-review** agent to review all changes on the branch. Address any critical issues before proceeding.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr/SKILL.md')
    assert '## Pre-PR Review' in text, "expected to find: " + '## Pre-PR Review'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **code-review** — Review code changes for quality and standards (auto-invoked before PR creation)' in text, "expected to find: " + '- **code-review** — Review code changes for quality and standards (auto-invoked before PR creation)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **spec-check** — Audit endpoints against W3C ActivityPub, SWICG, and FEP specs' in text, "expected to find: " + '- **spec-check** — Audit endpoints against W3C ActivityPub, SWICG, and FEP specs'[:80]

