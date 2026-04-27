"""Behavioral checks for master-skill-featcompare-divergence-radar-labeled-difference (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/master-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('prebuilt/compare/SKILL.md')
    assert '分歧雷达章节里列出的每一条具体差异，必须贴以下四种标签之一：`[宗派性分歧]` / `[侧重性分歧]` / `[表达性分歧]` / `[根器性分歧]`。无标签的差异描述视为未完成输出，必须补齐后才能呈现给用户。' in text, "expected to find: " + '分歧雷达章节里列出的每一条具体差异，必须贴以下四种标签之一：`[宗派性分歧]` / `[侧重性分歧]` / `[表达性分歧]` / `[根器性分歧]`。无标签的差异描述视为未完成输出，必须补齐后才能呈现给用户。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('prebuilt/compare/SKILL.md')
    assert '五维分歧雷达表格的 10 个单元格（2 位祖师 × 5 维）不得留空或填写"无"/"同上"。如某一维真的无法区分，应明确说明"此维两家殊途同归"，并归入`[表达性分歧]`类别。' in text, "expected to find: " + '五维分歧雷达表格的 10 个单元格（2 位祖师 × 5 维）不得留空或填写"无"/"同上"。如某一维真的无法区分，应明确说明"此维两家殊途同归"，并归入`[表达性分歧]`类别。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('prebuilt/compare/SKILL.md')
    assert '> 匹配规则：若用户问题命中以上论题关键词，`/compare-masters` **应主动提示**："这是佛教史上真实存在的论题，是否按经典论题模板展开？"' in text, "expected to find: " + '> 匹配规则：若用户问题命中以上论题关键词，`/compare-masters` **应主动提示**："这是佛教史上真实存在的论题，是否按经典论题模板展开？"'[:80]

