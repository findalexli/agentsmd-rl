"""Behavioral checks for ai-update-migration-skill-description-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md')
    assert 'reference, Call Control API guidance), messaging, WebRTC, number porting via' in text, "expected to find: " + 'reference, Call Control API guidance), messaging, WebRTC, number porting via'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md')
    assert 'FastPort, and Verify. Includes product mapping, migration scripts, and key' in text, "expected to find: " + 'FastPort, and Verify. Includes product mapping, migration scripts, and key'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('telnyx-twilio-migration/skills/telnyx-twilio-migration/SKILL.md')
    assert 'differences in auth, webhooks, and payload format.' in text, "expected to find: " + 'differences in auth, webhooks, and payload format.'[:80]

