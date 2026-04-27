"""Behavioral checks for bifrost-docs-add-pagination-support-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bifrost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-pr-comments/SKILL.md')
    assert '**Important:** `reviewThreads` returns at most 100 threads per request. PRs with many review threads (e.g. large CodeRabbit reviews) need **pagination** or you will only see the first 100 threads and ' in text, "expected to find: " + '**Important:** `reviewThreads` returns at most 100 threads per request. PRs with many review threads (e.g. large CodeRabbit reviews) need **pagination** or you will only see the first 100 threads and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-pr-comments/SKILL.md')
    assert 'After addressing comments, check remaining unresolved count. If the PR has more than 100 review threads, use the same pagination loop as in Step 2 and count unresolved across all pages; a single-page ' in text, "expected to find: " + 'After addressing comments, check remaining unresolved count. If the PR has more than 100 review threads, use the same pagination loop as in Step 2 and count unresolved across all pages; a single-page '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/resolve-pr-comments/SKILL.md')
    assert 'To reply to a review comment, use the dedicated replies endpoint. **Do not** use `POST .../pulls/PR_NUMBER/comments` with `in_reply_to` — that returns 422 (in_reply_to is not a permitted key for creat' in text, "expected to find: " + 'To reply to a review comment, use the dedicated replies endpoint. **Do not** use `POST .../pulls/PR_NUMBER/comments` with `in_reply_to` — that returns 422 (in_reply_to is not a permitted key for creat'[:80]

