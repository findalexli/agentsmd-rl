"""Behavioral checks for cli-featslidesdocument-supported-fonts (markdown_authoring task).

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
    text = _read('skills/lark-slides/references/supported-fonts.md')
    assert 'The XML schema accepts any string for `fontFamily`, but names outside this list may render with a fallback font.' in text, "expected to find: " + 'The XML schema accepts any string for `fontFamily`, but names outside this list may render with a fallback font.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-slides/references/supported-fonts.md')
    assert 'This document lists commonly supported `fontFamily` values for Lark Slides XML.' in text, "expected to find: " + 'This document lists commonly supported `fontFamily` values for Lark Slides XML.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-slides/references/supported-fonts.md')
    assert 'Use these names in `<theme><textStyles>` or `<content fontFamily="...">`.' in text, "expected to find: " + 'Use these names in `<theme><textStyles>` or `<content fontFamily="...">`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-slides/references/xml-schema-quick-ref.md')
    assert '> **字体兼容性**：`fontFamily` 的 schema 类型是字符串，但未列入 [supported-fonts.md](supported-fonts.md) 的字体可能在服务端或渲染端回退为默认字体。生成 PPT 时优先选用清单内字体。' in text, "expected to find: " + '> **字体兼容性**：`fontFamily` 的 schema 类型是字符串，但未列入 [supported-fonts.md](supported-fonts.md) 的字体可能在服务端或渲染端回退为默认字体。生成 PPT 时优先选用清单内字体。'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-slides/references/xml-schema-quick-ref.md')
    assert '> 常用默认字体：`思源黑体`（中文通用/默认）、`思源宋体`（中文正式/衬线）、`Inter`（拉丁通用）。' in text, "expected to find: " + '> 常用默认字体：`思源黑体`（中文通用/默认）、`思源宋体`（中文正式/衬线）、`Inter`（拉丁通用）。'[:80]

