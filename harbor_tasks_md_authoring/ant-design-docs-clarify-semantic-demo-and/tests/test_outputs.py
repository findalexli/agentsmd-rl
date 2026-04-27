"""Behavioral checks for ant-design-docs-clarify-semantic-demo-and (markdown_authoring task).

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
    assert '- `components/**/demo/_semantic*.tsx` 属于语义文档专用 demo，是例外场景：允许通过相对路径引用 `.dumi/hooks/useLocale`、`.dumi/theme/common/*` 等站点侧辅助模块。' in text, "expected to find: " + '- `components/**/demo/_semantic*.tsx` 属于语义文档专用 demo，是例外场景：允许通过相对路径引用 `.dumi/hooks/useLocale`、`.dumi/theme/common/*` 等站点侧辅助模块。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 常规 demo 与 `.dumi` 文件之间不要互相相对引用（`_semantic*.tsx` 等站点语义 demo 复用 `.dumi` 辅助模块除外）。如果需要复用少量逻辑，优先内联，或提取到可通过绝对路径访问的公共位置。' in text, "expected to find: " + '- 常规 demo 与 `.dumi` 文件之间不要互相相对引用（`_semantic*.tsx` 等站点语义 demo 复用 `.dumi` 辅助模块除外）。如果需要复用少量逻辑，优先内联，或提取到可通过绝对路径访问的公共位置。'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- 常规 demo 文件中，禁止使用 `..`、`../xxx`、`../../xxx`、`./xxx` 这类相对路径去引用组件实现、内部模块、方法、变量、类型，包含跨 demo、跨目录复用的场景。' in text, "expected to find: " + '- 常规 demo 文件中，禁止使用 `..`、`../xxx`、`../../xxx`、`./xxx` 这类相对路径去引用组件实现、内部模块、方法、变量、类型，包含跨 demo、跨目录复用的场景。'[:80]

