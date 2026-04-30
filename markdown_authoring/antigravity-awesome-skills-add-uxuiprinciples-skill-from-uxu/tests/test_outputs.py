"""Behavioral checks for antigravity-awesome-skills-add-uxuiprinciples-skill-from-uxu (markdown_authoring task).

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
    text = _read('skills/uxui-principles/SKILL.md')
    assert 'A collection of 5 agent skills for evaluating interfaces against 168 research-backed UX/UI principles, detecting antipatterns, and injecting UX context into AI-assisted design and coding sessions.' in text, "expected to find: " + 'A collection of 5 agent skills for evaluating interfaces against 168 research-backed UX/UI principles, detecting antipatterns, and injecting UX context into AI-assisted design and coding sessions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/uxui-principles/SKILL.md')
    assert 'description: "Evaluate interfaces against 168 research-backed UX/UI principles, detect antipatterns, and inject UX context into AI coding sessions."' in text, "expected to find: " + 'description: "Evaluate interfaces against 168 research-backed UX/UI principles, detect antipatterns, and inject UX context into AI coding sessions."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/uxui-principles/SKILL.md')
    assert '3. The skill evaluates against the relevant principles and returns structured findings with severity levels and remediation steps' in text, "expected to find: " + '3. The skill evaluates against the relevant principles and returns structured findings with severity levels and remediation steps'[:80]

