"""Behavioral checks for sitf-upddateing-the-techniqueproposal-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sitf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '| **V1.5** | Source Code Management Hardening | Branch protection, commit signing, code review |' in text, "expected to find: " + '| **V1.5** | Source Code Management Hardening | Branch protection, commit signing, code review |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '| **V1.2** | Hardening User Machines | IDE sandboxing, app whitelisting, credential storage |' in text, "expected to find: " + '| **V1.2** | Hardening User Machines | IDE sandboxing, app whitelisting, credential storage |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/technique-proposal/SKILL.md')
    assert '"description": "Remove or disable flags like --dangerously-skip-permissions from AI tools",' in text, "expected to find: " + '"description": "Remove or disable flags like --dangerously-skip-permissions from AI tools",'[:80]

