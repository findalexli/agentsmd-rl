"""Behavioral checks for compound-engineering-plugin-fixskills-update-ralphwiggum-ref (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/lfg/SKILL.md')
    assert '1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2' in text, "expected to find: " + '1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/lfg/SKILL.md')
    assert 'Start with step 2 now (or step 1 if ralph-loop is available). Remember: plan FIRST, then work. Never skip the plan.' in text, "expected to find: " + 'Start with step 2 now (or step 1 if ralph-loop is available). Remember: plan FIRST, then work. Never skip the plan.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/slfg/SKILL.md')
    assert '1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2' in text, "expected to find: " + '1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2'[:80]

