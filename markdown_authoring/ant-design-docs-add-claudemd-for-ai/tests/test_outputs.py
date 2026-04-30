"""Behavioral checks for ant-design-docs-add-claudemd-for-ai (markdown_authoring task).

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
    text = _read('CLAUDE.md')
    assert '- 🐞 Fix Button reversed `hover` and `active` colors for `color` in dark theme. [#56872](link) [@zombieJ](link)' in text, "expected to find: " + '- 🐞 Fix Button reversed `hover` and `active` colors for `color` in dark theme. [#56872](link) [@zombieJ](link)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| 英文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 Fix Button reversed \\`hover\\` colors in dark theme.` |' in text, "expected to find: " + '| 英文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 Fix Button reversed \\`hover\\` colors in dark theme.` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 🐞 Button 修复暗色主题下 `color` 的 `hover` 与 `active` 状态颜色相反的问题。[#56872](链接) [@zombieJ](链接)' in text, "expected to find: " + '- 🐞 Button 修复暗色主题下 `color` 的 `hover` 与 `active` 状态颜色相反的问题。[#56872](链接) [@zombieJ](链接)'[:80]

