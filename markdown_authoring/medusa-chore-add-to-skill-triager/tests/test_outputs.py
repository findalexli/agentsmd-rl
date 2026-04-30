"""Behavioral checks for medusa-chore-add-to-skill-triager (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/medusa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/reviewing-prs/SKILL.md')
    assert '- [ ] Approving a PR that changes behavior documented as intentional — always check the docs when a PR modifies existing behavior; if the docs describe it as by design, flag it as `requires-more`' in text, "expected to find: " + '- [ ] Approving a PR that changes behavior documented as intentional — always check the docs when a PR modifies existing behavior; if the docs describe it as by design, flag it as `requires-more`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/reviewing-prs/reference/comment-guidelines.md')
    assert '- **Is the behavior being changed intentional and documented?** If the PR modifies existing behavior, check whether that behavior is described as by design in the official Medusa documentation (`www/a' in text, "expected to find: " + '- **Is the behavior being changed intentional and documented?** If the PR modifies existing behavior, check whether that behavior is described as by design in the official Medusa documentation (`www/a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/triaging-issues/SKILL.md')
    assert '- [ ] Confirming a bug without first checking the documentation — always check if the behavior is documented as intentional before treating it as a bug' in text, "expected to find: " + '- [ ] Confirming a bug without first checking the documentation — always check if the behavior is documented as intentional before treating it as a bug'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/triaging-issues/reference/bug-report.md')
    assert '> **CRITICAL:** Before treating anything as a bug, check the official Medusa documentation to determine if the reported behavior is **intentional and documented**. Do this actively — search the docs a' in text, "expected to find: " + '> **CRITICAL:** Before treating anything as a bug, check the official Medusa documentation to determine if the reported behavior is **intentional and documented**. Do this actively — search the docs a'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/triaging-issues/reference/bug-report.md')
    assert 'Read the relevant documentation section (e.g. `www/apps/book/app/learn/fundamentals/`) for the feature mentioned in the issue. Ask: "Is the behavior the user is reporting described as by design anywhe' in text, "expected to find: " + 'Read the relevant documentation section (e.g. `www/apps/book/app/learn/fundamentals/`) for the feature mentioned in the issue. Ask: "Is the behavior the user is reporting described as by design anywhe'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/triaging-issues/reference/bug-report.md')
    assert '**If the behavior is undocumented or the docs are unclear/misleading** (but it still turns out to be by design after codebase review), treat it as a documentation gap — see Step 3 below.' in text, "expected to find: " + '**If the behavior is undocumented or the docs are unclear/misleading** (but it still turns out to be by design after codebase review), treat it as a documentation gap — see Step 3 below.'[:80]

