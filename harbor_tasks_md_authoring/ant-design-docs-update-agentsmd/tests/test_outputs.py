"""Behavioral checks for ant-design-docs-update-agentsmd (markdown_authoring task).

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
    assert '- 测试文件应优先从当前组件目录、相邻内部模块或共享测试工具目录通过相对路径引用，例如：`..`、`../index`、`../xxx`、`../../_util/*`、`../../../tests/shared/*`。' in text, "expected to find: " + '- 测试文件应优先从当前组件目录、相邻内部模块或共享测试工具目录通过相对路径引用，例如：`..`、`../index`、`../xxx`、`../../_util/*`、`../../../tests/shared/*`。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 禁止在 `__tests__` 目录下使用 `antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*` 这类绝对路径或别名路径去引用仓库内代码。' in text, "expected to find: " + '- 禁止在 `__tests__` 目录下使用 `antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*` 这类绝对路径或别名路径去引用仓库内代码。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 允许的导入形式应优先使用项目公开入口或已配置别名，例如：`antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*`。' in text, "expected to find: " + '- 允许的导入形式应优先使用项目公开入口或已配置别名，例如：`antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*`。'[:80]

