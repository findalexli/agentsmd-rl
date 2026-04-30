"""Behavioral checks for last30days-skill-fix-enforce-preresearch-protocol-override (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/last30days-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**MANDATORY — bold headline per narrative paragraph.** Every paragraph in the "What I learned" section MUST begin with a bolded headline phrase that summarizes the paragraph, followed by a dash and th' in text, "expected to find: " + '**MANDATORY — bold headline per narrative paragraph.** Every paragraph in the "What I learned" section MUST begin with a bolded headline phrase that summarizes the paragraph, followed by a dash and th'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "7. **Research protocol was followed.** On WebSearch platforms, the command you ran used `--emit=compact --plan 'QUERY_PLAN_JSON'` with resolved handles/subreddits/hashtags. If you took the degraded pa" in text, "expected to find: " + "7. **Research protocol was followed.** On WebSearch platforms, the command you ran used `--emit=compact --plan 'QUERY_PLAN_JSON'` with resolved handles/subreddits/hashtags. If you took the degraded pa"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '2. **If WebSearch IS available:** you MUST have run Step 0.55 (Pre-Research Intelligence — resolved subreddits, X handles, TikTok hashtags/creators, Instagram creators, GitHub user/repo where applicab' in text, "expected to find: " + '2. **If WebSearch IS available:** you MUST have run Step 0.55 (Pre-Research Intelligence — resolved subreddits, X handles, TikTok hashtags/creators, Instagram creators, GitHub user/repo where applicab'[:80]

