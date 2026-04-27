"""Behavioral checks for antigravity-awesome-skills-feat-add-vibecodeauditor-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vibe-code-auditor/SKILL.md')
    assert 'description: When the user wants to audit rapidly generated or AI-produced code for structural flaws, fragility, and production risks. Use when code was written by AI tools, evolved without deliberate' in text, "expected to find: " + 'description: When the user wants to audit rapidly generated or AI-produced code for structural flaws, fragility, and production risks. Use when code was written by AI tools, evolved without deliberate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vibe-code-auditor/SKILL.md')
    assert 'Evaluate the code across all seven dimensions below. For each finding, record: the dimension, a short title, the exact location (file and line number if available), the severity, a clear explanation, ' in text, "expected to find: " + 'Evaluate the code across all seven dimensions below. For each finding, record: the dimension, a short title, the exact location (file and line number if available), the severity, a clear explanation, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/vibe-code-auditor/SKILL.md')
    assert '- Report the location (file and line) of each finding whenever the information is available. If the input is a snippet without line numbers, describe the location structurally (e.g., "inside the `proc' in text, "expected to find: " + '- Report the location (file and line) of each finding whenever the information is available. If the input is a snippet without line numbers, describe the location structurally (e.g., "inside the `proc'[:80]

