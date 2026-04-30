"""Behavioral checks for nanostack-simplify-autopilot-to-sequential-flow (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert 'Proceed directly to `/review`. After review completes, run `/security`. After security, run `/qa`. After all three pass, run `/ship`. Only stop if:' in text, "expected to find: " + 'Proceed directly to `/review`. After review completes, run `/security`. After security, run `/qa`. After all three pass, run `/ship`. Only stop if:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert 'For parallel execution across multiple terminals, use `/conductor` instead of autopilot.' in text, "expected to find: " + 'For parallel execution across multiple terminals, use `/conductor` instead of autopilot.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert "- A product question comes up that you can't answer from context" in text, "expected to find: " + "- A product question comes up that you can't answer from context"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**If AUTOPILOT is active and tests pass:** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`' in text, "expected to find: " + '**If AUTOPILOT is active and tests pass:** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**If AUTOPILOT is active but tests fail:** Stop and ask the user. Show failures and wait.' in text, "expected to find: " + '**If AUTOPILOT is active but tests fail:** Stop and ask the user. Show failures and wait.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '**If AUTOPILOT is active and no blocking issues found:** Proceed directly to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /securit' in text, "expected to find: " + '**If AUTOPILOT is active and no blocking issues found:** Proceed directly to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /securit'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '**If AUTOPILOT is active but blocking issues found:** Stop and ask the user to resolve. Show the blocking issues and wait. After resolution, continue autopilot.' in text, "expected to find: " + '**If AUTOPILOT is active but blocking issues found:** Stop and ask the user to resolve. Show the blocking issues and wait. After resolution, continue autopilot.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '**If AUTOPILOT is active and no critical/high findings:** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`' in text, "expected to find: " + '**If AUTOPILOT is active and no critical/high findings:** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '**If AUTOPILOT is active but critical or high findings found:** Stop and ask the user to review. Show the findings and wait. After resolution, continue autopilot.' in text, "expected to find: " + '**If AUTOPILOT is active but critical or high findings found:** Stop and ask the user to review. Show the findings and wait. After resolution, continue autopilot.'[:80]

