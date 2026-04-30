"""Behavioral checks for vibe-remote-fixskills-clarify-vibe-remote-dm (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-remote")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert 'Important DM caveat: current DM authorization checks whether the user is bound, not whether `scopes.user.<platform>.<user_id>.enabled` is `true`. If the user wants to revoke DM access, do not rely on ' in text, "expected to find: " + 'Important DM caveat: current DM authorization checks whether the user is bound, not whether `scopes.user.<platform>.<user_id>.enabled` is `true`. If the user wants to revoke DM access, do not rely on '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert 'If the user wants to revoke an existing DM binding, treat that as a bind-state change rather than a normal settings toggle. In the current implementation, removing the user entry is the reliable way t' in text, "expected to find: " + 'If the user wants to revoke an existing DM binding, treat that as a bind-state change rather than a normal settings toggle. In the current implementation, removing the user entry is the reliable way t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/use-vibe-remote/SKILL.md')
    assert 'If the user still cannot solve a problem after normal config fixes, `vibe doctor`, restart, and log inspection, point them to the Vibe Remote repository:' in text, "expected to find: " + 'If the user still cannot solve a problem after normal config fixes, `vibe doctor`, restart, and log inspection, point them to the Vibe Remote repository:'[:80]

