"""Behavioral checks for tilelang-ascend-pass-designascendlowerparalleltovector-desig (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tilelang-ascend")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_lower_parallel_to_vector_design.md')
    assert 'T.Parallel 就是用于描述这一 Compute 阶段的 tile内元素向量化计算 的结构化语义。而 ascend_lower_parallel_to_vector.cc 则是实现 T.Parallel 功能的 pass。' in text, "expected to find: " + 'T.Parallel 就是用于描述这一 Compute 阶段的 tile内元素向量化计算 的结构化语义。而 ascend_lower_parallel_to_vector.cc 则是实现 T.Parallel 功能的 pass。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_lower_parallel_to_vector_design.md')
    assert '| C++ 实现 | `src/transform/ascend_lower_parallel_to_vector.cc` | `AscendLowerParallelToVector::Substitute()` |' in text, "expected to find: " + '| C++ 实现 | `src/transform/ascend_lower_parallel_to_vector.cc` | `AscendLowerParallelToVector::Substitute()` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_lower_parallel_to_vector_design.md')
    assert '- 新增的 T.tile.xxx 接口，内容为原 ascend.py 中的 vector 操作（集中放在 ascend_tile.py 中），保留 TileLang-Ascend 中 vector 原语能力' in text, "expected to find: " + '- 新增的 T.tile.xxx 接口，内容为原 ascend.py 中的 vector 操作（集中放在 ascend_tile.py 中），保留 TileLang-Ascend 中 vector 原语能力'[:80]

