"""Behavioral checks for atcoderclans-feat-add-milestonecheck-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/atcoderclans")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '- `milestone-check` — detect users who newly crossed a rating threshold after a contest' in text, "expected to find: " + '- `milestone-check` — detect users who newly crossed a rating threshold after a contest'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '- `.claude/rules/` — persistent behavioral rules loaded in every session' in text, "expected to find: " + '- `.claude/rules/` — persistent behavioral rules loaded in every session'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '- `.claude/skills/` — invocable skills (use `/skill-name` to trigger)' in text, "expected to find: " + '- `.claude/skills/` — invocable skills (use `/skill-name` to trigger)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/workflow.md')
    assert 'After an AtCoder contest, use `/milestone-check <contest_id>` to detect newly eligible' in text, "expected to find: " + 'After an AtCoder contest, use `/milestone-check <contest_id>` to detect newly eligible'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/workflow.md')
    assert 'blog candidates. See `.claude/skills/milestone-check/` for details.' in text, "expected to find: " + 'blog candidates. See `.claude/skills/milestone-check/` for details.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/workflow.md')
    assert '## Milestone check after contests' in text, "expected to find: " + '## Milestone check after contests'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/SKILL.md')
    assert "AtCoder contest, validate whether they are listed on the site's blog pages, and report" in text, "expected to find: " + "AtCoder contest, validate whether they are listed on the site's blog pages, and report"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/SKILL.md')
    assert 'Validate an AtCoder contest for users who newly reached a rating milestone, and report' in text, "expected to find: " + 'Validate an AtCoder contest for users who newly reached a rating milestone, and report'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/SKILL.md')
    assert 'Read `.claude/skills/milestone-check/instructions.md` and follow Steps 1–5 in order.' in text, "expected to find: " + 'Read `.claude/skills/milestone-check/instructions.md` and follow Steps 1–5 in order.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/instructions.md')
    assert '| **Listed, section correct**        | Listed section matches current highest rating → no change needed |' in text, "expected to find: " + '| **Listed, section correct**        | Listed section matches current highest rating → no change needed |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/instructions.md')
    assert '| Status                             | Description                                                    |' in text, "expected to find: " + '| Status                             | Description                                                    |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/milestone-check/instructions.md')
    assert '| **Unlisted**                       | Not found in any file → proceed to Step 4                      |' in text, "expected to find: " + '| **Unlisted**                       | Not found in any file → proceed to Step 4                      |'[:80]

