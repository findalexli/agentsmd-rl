"""Behavioral checks for antigravity-awesome-skills-feat-add-linkedinprofileoptimizer (markdown_authoring task).

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
    text = _read('skills/linkedin-profile-optimizer/SKILL.md')
    assert '> "I recognize the LinkedIn handle `whoisabhishekadhikari`. Before I perform an audit, I need to verify your current profile data. I have attempted to fetch your public profile [Link]. **However, if y' in text, "expected to find: " + '> "I recognize the LinkedIn handle `whoisabhishekadhikari`. Before I perform an audit, I need to verify your current profile data. I have attempted to fetch your public profile [Link]. **However, if y'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/linkedin-profile-optimizer/SKILL.md')
    assert '- **Hallucination Prevention**: If only a username/handle is provided, you **MUST** verify you can access the profile using your browsing tool. If the profile is private, inaccessible, or your browsin' in text, "expected to find: " + '- **Hallucination Prevention**: If only a username/handle is provided, you **MUST** verify you can access the profile using your browsing tool. If the profile is private, inaccessible, or your browsin'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/linkedin-profile-optimizer/SKILL.md')
    assert 'This skill helps professionals (founders, lecturers, IT experts, and agritech builders) align their core identity, remove brand confusion, and attract global opportunities by synthesizing information ' in text, "expected to find: " + 'This skill helps professionals (founders, lecturers, IT experts, and agritech builders) align their core identity, remove brand confusion, and attract global opportunities by synthesizing information '[:80]

