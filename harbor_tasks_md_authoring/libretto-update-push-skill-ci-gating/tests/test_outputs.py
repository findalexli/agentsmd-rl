"""Behavioral checks for libretto-update-push-skill-ci-gating (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert 'For follow-up edits in this session, continue to commit, push, and update the PR as needed. After each follow-up push, re-run the full check-wait loop above (`gh pr checks --watch` and retries) before' in text, "expected to find: " + 'For follow-up edits in this session, continue to commit, push, and update the PR as needed. After each follow-up push, re-run the full check-wait loop above (`gh pr checks --watch` and retries) before'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert '2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total).' in text, "expected to find: " + '2. If GitHub returns `no checks reported`, treat it as possible propagation delay. Wait 15 seconds and retry `gh pr checks --watch`. Repeat up to 8 times (about 2 minutes total).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/push/SKILL.md')
    assert '6. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.' in text, "expected to find: " + '6. If any test or type-check command fails, inspect logs immediately, fix the issue, commit, push, and repeat this CI loop until checks pass.'[:80]

