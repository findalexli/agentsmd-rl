"""Behavioral checks for compound-engineering-plugin-fixskills-plan-is-a-decision (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-code-review/SKILL.md')
    assert 'If a plan is found, read its **Requirements Trace** (R1, R2, etc.) and **Implementation Units** (items listed under the `## Implementation Units` section). Store the extracted requirements list and `p' in text, "expected to find: " + 'If a plan is found, read its **Requirements Trace** (R1, R2, etc.) and **Implementation Units** (items listed under the `## Implementation Units` section). Store the extracted requirements list and `p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-code-review/SKILL.md')
    assert '- `docs/plans/*.md` -- plan files created by ce-plan (decision artifacts; execution progress is derived from git, not stored in plan bodies)' in text, "expected to find: " + '- `docs/plans/*.md` -- plan files created by ce-plan (decision artifacts; execution progress is derived from git, not stored in plan bodies)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert "Each unit's heading carries a stable U-ID prefix matching the format used for R/A/F/AE in requirements docs: `- U1. **[Name]**`. The prefix is plain text, not bolded — the bold is reserved for the uni" in text, "expected to find: " + "Each unit's heading carries a stable U-ID prefix matching the format used for R/A/F/AE in requirements docs: `- U1. **[Name]**`. The prefix is plain text, not bolded — the bold is reserved for the uni"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '- If updating, revise only the still-relevant sections. Plans do not carry per-unit progress state — progress is derived from git by `ce-work`, so there is no progress to preserve across edits' in text, "expected to find: " + '- If updating, revise only the still-relevant sections. Plans do not carry per-unit progress state — progress is derived from git by `ce-work`, so there is no progress to preserve across edits'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '- U1. **[Name]**' in text, "expected to find: " + '- U1. **[Name]**'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '- **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: activ' in text, "expected to find: " + '- **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: activ'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert "- **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), t" in text, "expected to find: " + "- **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), t"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work-beta/SKILL.md')
    assert '5. Update the task list (do not edit the plan body — progress is carried by the commits just made)' in text, "expected to find: " + '5. Update the task list (do not edit the plan body — progress is carried by the commits just made)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '- **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: activ' in text, "expected to find: " + '- **Do not edit the plan body during execution.** The plan is a decision artifact; progress lives in git commits and the task tracker. The only plan mutation during ce-work is the final `status: activ'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert "- **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), t" in text, "expected to find: " + "- **If the unit's work is already present and matches the plan's intent** (files exist with the expected capability, or the unit's `Verification` criteria are already satisfied by the current code), t"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-work/SKILL.md')
    assert '5. Update the task list (do not edit the plan body — progress is carried by the commits just made)' in text, "expected to find: " + '5. Update the task list (do not edit the plan body — progress is carried by the commits just made)'[:80]

