"""Behavioral checks for github-copilot-for-azure-strengthen-planfirst-enforcement-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-copilot-for-azure")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-prepare/SKILL.md')
    assert '1. **Plan first — MANDATORY** — You MUST physically write an initial `.azure/deployment-plan.md` **skeleton in the workspace root directory** (not the session-state folder) **as your very first action' in text, "expected to find: " + '1. **Plan first — MANDATORY** — You MUST physically write an initial `.azure/deployment-plan.md` **skeleton in the workspace root directory** (not the session-state folder) **as your very first action'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-prepare/SKILL.md')
    assert '> ⚠️ **CRITICAL: `.azure/deployment-plan.md` must be WRITTEN TO DISK inside the workspace root** (e.g., `/tmp/my-project/.azure/deployment-plan.md`), not in the session-state folder. Use a file-write ' in text, "expected to find: " + '> ⚠️ **CRITICAL: `.azure/deployment-plan.md` must be WRITTEN TO DISK inside the workspace root** (e.g., `/tmp/my-project/.azure/deployment-plan.md`), not in the session-state folder. Use a file-write '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugin/skills/azure-prepare/SKILL.md')
    assert '| 6 | **Finalize Plan (MANDATORY)** - Use a file-write tool to finalize `.azure/deployment-plan.md` with all decisions from steps 1-5. Update the skeleton written at the start of Phase 1 with the comp' in text, "expected to find: " + '| 6 | **Finalize Plan (MANDATORY)** - Use a file-write tool to finalize `.azure/deployment-plan.md` with all decisions from steps 1-5. Update the skeleton written at the start of Phase 1 with the comp'[:80]

