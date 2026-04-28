"""Behavioral checks for tilelang-ascend-add-tilelang-pass-design-skill (markdown_authoring task).

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
    text = _read('.agents/skills/tilelang-pass-design/SKILL.md')
    assert 'description: "根据 Pass 需求生成 TileLang-Ascend Pass 设计文档（pass-design.md）。涵盖 Pass 定位分析（Phase 1/2归属、Pipeline位置、依赖关系）、IR 变换设计、C++ 实现方案、测试方案、风险分析等。触发关键词：设计 Pass、Pass 设计文档、写 Pass、实现 Pass、添加 Pass、新建 Pass、Pass 设' in text, "expected to find: " + 'description: "根据 Pass 需求生成 TileLang-Ascend Pass 设计文档（pass-design.md）。涵盖 Pass 定位分析（Phase 1/2归属、Pipeline位置、依赖关系）、IR 变换设计、C++ 实现方案、测试方案、风险分析等。触发关键词：设计 Pass、Pass 设计文档、写 Pass、实现 Pass、添加 Pass、新建 Pass、Pass 设'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/SKILL.md')
    assert '| Pipeline 架构 | `tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md` | 阶段划分、Pass 列表 |' in text, "expected to find: " + '| Pipeline 架构 | `tilelang-pass-workflow-analyzer/references/pass-pipeline-overview.md` | 阶段划分、Pass 列表 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/SKILL.md')
    assert '| Pass 定位指南 | `tilelang-pass-workflow-analyzer/references/new-pass-placement-guide.md` | 定位决策流程 |' in text, "expected to find: " + '| Pass 定位指南 | `tilelang-pass-workflow-analyzer/references/new-pass-placement-guide.md` | 定位决策流程 |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md')
    assert '| `buffer scope annotations` | `Map<Buffer, String>` | `AscendInferBufferScope` | `CrossCorePipeline`, `CombineCV` |' in text, "expected to find: " + '| `buffer scope annotations` | `Map<Buffer, String>` | `AscendInferBufferScope` | `CrossCorePipeline`, `CombineCV` |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md')
    assert '| `AscendLowerParallelToVector` | `ascend_lower_parallel_to_vector.cc` | ~2000 | Parallel lowering |' in text, "expected to find: " + '| `AscendLowerParallelToVector` | `ascend_lower_parallel_to_vector.cc` | ~2000 | Parallel lowering |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md')
    assert '| `buffer_shapess` | `Map<Var, Array<PrimExpr>>` | `CollectBufferShapes` | `AscendMemoryPlanning` |' in text, "expected to find: " + '| `buffer_shapess` | `Map<Var, Array<PrimExpr>>` | `CollectBufferShapes` | `AscendMemoryPlanning` |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/templates/pass-design-template.md')
    assert '| {buffer_shapess} | `CollectBufferShapes` | Phase 1 步骤 8 | `f->GetAttr<Map<Var, Array<PrimExpr>>>(...)` |' in text, "expected to find: " + '| {buffer_shapess} | `CollectBufferShapes` | Phase 1 步骤 8 | `f->GetAttr<Map<Var, Array<PrimExpr>>>(...)` |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/templates/pass-design-template.md')
    assert '| {buffer scope} | `AscendInferBufferScope` | Phase 1 步骤 1 | `f->GetAttr<Map<...>>(...)` |' in text, "expected to find: " + '| {buffer scope} | `AscendInferBufferScope` | Phase 1 步骤 1 | `f->GetAttr<Map<...>>(...)` |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-design/templates/pass-design-template.md')
    assert '| {address_map} | `AscendMemoryPlanning` | Phase 2 步骤 20 | `f->GetAttr<Map<...>>(...)` |' in text, "expected to find: " + '| {address_map} | `AscendMemoryPlanning` | Phase 2 步骤 20 | `f->GetAttr<Map<...>>(...)` |'[:80]

