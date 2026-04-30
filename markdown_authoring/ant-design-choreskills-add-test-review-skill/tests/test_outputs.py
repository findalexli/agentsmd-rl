"""Behavioral checks for ant-design-choreskills-add-test-review-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ant-design")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/test-review/SKILL.md')
    assert 'description: 审查 ant-design 测试用例是否值得保留。在用户要求验证测试 case、review 测试质量、判断测试是否合理、是否“用 A 证明 A”、是否重复、是否锁定实现细节，或决定测试应删除、保留还是改写时使用。' in text, "expected to find: " + 'description: 审查 ant-design 测试用例是否值得保留。在用户要求验证测试 case、review 测试质量、判断测试是否合理、是否“用 A 证明 A”、是否重复、是否锁定实现细节，或决定测试应删除、保留还是改写时使用。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/test-review/SKILL.md')
    assert 'rg -n "<关键字>|<issue号>|<行为描述>" components/<component> tests' in text, "expected to find: " + 'rg -n "<关键字>|<issue号>|<行为描述>" components/<component> tests'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/test-review/SKILL.md')
    assert "- `expect(node).toHaveStyle({ whiteSpace: 'nowrap' })`" in text, "expected to find: " + "- `expect(node).toHaveStyle({ whiteSpace: 'nowrap' })`"[:80]

