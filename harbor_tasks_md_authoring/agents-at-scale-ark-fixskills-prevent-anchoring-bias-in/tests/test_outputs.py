"""Behavioral checks for agents-at-scale-ark-fixskills-prevent-anchoring-bias-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agents-at-scale-ark")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-creation/SKILL.md')
    assert '3. **Research informs scope, not implementation.** Codebase research belongs in the Context section to help the implementer orient. It must NOT leak into the Task Breakdown as prescriptive implementat' in text, "expected to find: " + '3. **Research informs scope, not implementation.** Codebase research belongs in the Context section to help the implementer orient. It must NOT leak into the Task Breakdown as prescriptive implementat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-creation/SKILL.md')
    assert "**Important:** The purpose of research is to understand the problem's scope and surface area — NOT to prescribe a solution. Do not let research findings leak into prescriptive implementation tasks. Kn" in text, "expected to find: " + "**Important:** The purpose of research is to understand the problem's scope and surface area — NOT to prescribe a solution. Do not let research findings leak into prescriptive implementation tasks. Kn"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue-creation/SKILL.md')
    assert '4. **Tasks describe WHAT, not HOW.** Each task should describe a problem to solve or a behavior to achieve. Bad: "Add sanitization in `services/ark-api/handlers/query.go`". Good: "Handle special chara' in text, "expected to find: " + '4. **Tasks describe WHAT, not HOW.** Each task should describe a problem to solve or a behavior to achieve. Bad: "Add sanitization in `services/ark-api/handlers/query.go`". Good: "Handle special chara'[:80]

