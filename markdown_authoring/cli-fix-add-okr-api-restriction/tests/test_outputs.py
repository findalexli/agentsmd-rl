"""Behavioral checks for cli-fix-add-okr-api-restriction (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-okr/SKILL.md')
    assert '- 对齐不允许对齐自己的目标，且发起对齐的目标和被对齐的目标所在周期时间上必须有重叠，否则会参数校验失败。' in text, "expected to find: " + '- 对齐不允许对齐自己的目标，且发起对齐的目标和被对齐的目标所在周期时间上必须有重叠，否则会参数校验失败。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-okr/SKILL.md')
    assert '- 请求中必须同时修改对应目标下全部关键结果的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。' in text, "expected to find: " + '- 请求中必须同时修改对应目标下全部关键结果的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-okr/SKILL.md')
    assert '- 请求中必须同时修改对应周期下全部目标的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。' in text, "expected to find: " + '- 请求中必须同时修改对应周期下全部目标的权重，且所有权重值的和必须等于 1 ，否则会参数校验失败。'[:80]

