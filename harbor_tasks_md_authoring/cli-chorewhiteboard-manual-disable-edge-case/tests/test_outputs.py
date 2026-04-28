"""Behavioral checks for cli-chorewhiteboard-manual-disable-edge-case (markdown_authoring task).

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
    text = _read('skills/lark-whiteboard/references/lark-whiteboard-update.md')
    assert '思维导图，时序图，类图，饼图，流程图等图表推荐使用 Mermaid/PlantUML 语法绘制。' in text, "expected to find: " + '思维导图，时序图，类图，饼图，流程图等图表推荐使用 Mermaid/PlantUML 语法绘制。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '画板的 svg-parser 把可识别元素转成可编辑节点, 其余降级为内嵌图片(渲染没问题, 虽然不可编辑, 但是可以正常显示)；但 `<radialGradient>` / `<filter>` / `<clipPath>` 等装饰特性画板完全不支持，会导致渲染问题（见下方⚠️）' in text, "expected to find: " + '画板的 svg-parser 把可识别元素转成可编辑节点, 其余降级为内嵌图片(渲染没问题, 虽然不可编辑, 但是可以正常显示)；但 `<radialGradient>` / `<filter>` / `<clipPath>` 等装饰特性画板完全不支持，会导致渲染问题（见下方⚠️）'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '- `<radialGradient>` / `<filter>` / `<pattern>` / `<clipPath>` / `<mask>` → 画板都不支持，**请避免使用，否则会导致画板渲染问题**' in text, "expected to find: " + '- `<radialGradient>` / `<filter>` / `<pattern>` / `<clipPath>` / `<mask>` → 画板都不支持，**请避免使用，否则会导致画板渲染问题**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-whiteboard/routes/svg.md')
    assert '**不需要所有元素都可编辑, 但必须避免使用不支持的装饰特性, 且要兼顾可编辑和美观漂亮**' in text, "expected to find: " + '**不需要所有元素都可编辑, 但必须避免使用不支持的装饰特性, 且要兼顾可编辑和美观漂亮**'[:80]

