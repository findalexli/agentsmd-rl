"""Behavioral checks for antigravity-awesome-skills-feat-add-viberscodereview-for-hum (markdown_authoring task).

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
    text = _read('skills/vibers-code-review/SKILL.md')
    assert '| `spec_url` | Link to your spec (Google Doc, Notion, etc.). **Must be publicly accessible** (or "anyone with the link can view"). Without access to spec, review is impossible. |' in text, "expected to find: " + '| `spec_url` | Link to your spec (Google Doc, Notion, etc.). **Must be publicly accessible** (or "anyone with the link can view"). Without access to spec, review is impossible. |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vibers-code-review/SKILL.md')
    assert 'description: Human review workflow for AI-generated GitHub projects with spec-based feedback, security review, and follow-up PRs from the Vibers service.' in text, "expected to find: " + 'description: Human review workflow for AI-generated GitHub projects with spec-based feedback, security review, and follow-up PRs from the Vibers service.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vibers-code-review/SKILL.md')
    assert 'We check: spec compliance, security (OWASP top 10), AI hallucinations (fake APIs/imports), logic bugs, UI issues.' in text, "expected to find: " + 'We check: spec compliance, security (OWASP top 10), AI hallucinations (fake APIs/imports), logic bugs, UI issues.'[:80]

