"""Behavioral checks for antigravity-awesome-skills-feat-add-apidocumentationgenerato (markdown_authoring task).

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
    text = _read('skills/api-documentation-generator/SKILL.md')
    assert 'Automatically generate clear, comprehensive API documentation from your codebase. This skill helps you create professional documentation that includes endpoint descriptions, request/response examples,' in text, "expected to find: " + 'Automatically generate clear, comprehensive API documentation from your codebase. This skill helps you create professional documentation that includes endpoint descriptions, request/response examples,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/api-documentation-generator/SKILL.md')
    assert '**Pro Tip:** Keep your API documentation as close to your code as possible. Use tools that generate docs from code comments to ensure they stay in sync!' in text, "expected to find: " + '**Pro Tip:** Keep your API documentation as close to your code as possible. Use tools that generate docs from code comments to ensure they stay in sync!'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/api-documentation-generator/SKILL.md')
    assert 'description: "Generate comprehensive, developer-friendly API documentation from code, including endpoints, parameters, examples, and best practices"' in text, "expected to find: " + 'description: "Generate comprehensive, developer-friendly API documentation from code, including endpoints, parameters, examples, and best practices"'[:80]

