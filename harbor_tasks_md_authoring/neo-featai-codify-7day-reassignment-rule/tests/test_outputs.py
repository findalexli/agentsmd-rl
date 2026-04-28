"""Behavioral checks for neo-featai-codify-7day-reassignment-rule (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ticket-intake/references/ticket-intake-workflow.md')
    assert '- **If `now - lastQualifyingActivity >= 7 days`:** Proceed with self-serve reassignment. You MUST post a mandatory attribution comment first: *"Picking up per 7-day rule; previous assignee @X; last qu' in text, "expected to find: " + '- **If `now - lastQualifyingActivity >= 7 days`:** Proceed with self-serve reassignment. You MUST post a mandatory attribution comment first: *"Picking up per 7-day rule; previous assignee @X; last qu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ticket-intake/references/ticket-intake-workflow.md')
    assert '- Compute `lastQualifyingActivity`: The most recent comment from the current assignee OR from any maintainer (`@neo-opus-4-7`, `@neo-gemini-3-1-pro`, or contributor with write permissions) acknowledgi' in text, "expected to find: " + '- Compute `lastQualifyingActivity`: The most recent comment from the current assignee OR from any maintainer (`@neo-opus-4-7`, `@neo-gemini-3-1-pro`, or contributor with write permissions) acknowledgi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/ticket-intake/references/ticket-intake-workflow.md')
    assert 'Signal to the Swarm that this ticket is actively being worked. Before assigning yourself, you MUST verify that the ticket is not already owned by another active agent or human.' in text, "expected to find: " + 'Signal to the Swarm that this ticket is actively being worked. Before assigning yourself, you MUST verify that the ticket is not already owned by another active agent or human.'[:80]

