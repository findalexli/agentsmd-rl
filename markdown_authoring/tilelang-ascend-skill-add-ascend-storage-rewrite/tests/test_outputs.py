"""Behavioral checks for tilelang-ascend-skill-add-ascend-storage-rewrite (markdown_authoring task).

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
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_storage_rewrite_design.md')
    assert '3. 保留 Ascend 语义修正：在 rewrite 后继续透传 `tl.local_var_init` [src/transform/ascend_storage_rewrite.cc](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/src/transform/ascend_storage_rewrite.cc#L193' in text, "expected to find: " + '3. 保留 Ascend 语义修正：在 rewrite 后继续透传 `tl.local_var_init` [src/transform/ascend_storage_rewrite.cc](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/src/transform/ascend_storage_rewrite.cc#L193'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_storage_rewrite_design.md')
    assert '* Python/FFI 暴露改动：在 [tilelang/transform/__init__.py](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/tilelang/transform/__init__.py#L482) 中新增 `AscendStorageRewrite(is_npu: bool = False)`，并' in text, "expected to find: " + '* Python/FFI 暴露改动：在 [tilelang/transform/__init__.py](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/tilelang/transform/__init__.py#L482) 中新增 `AscendStorageRewrite(is_npu: bool = False)`，并'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/ascend_storage_rewrite_design.md')
    assert '* 注解透传改动：在 [src/transform/ascend_storage_rewrite.cc](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/src/transform/ascend_storage_rewrite.cc#L1937) 读取 `tl.local_var_init`，并通过 [src/transfor' in text, "expected to find: " + '* 注解透传改动：在 [src/transform/ascend_storage_rewrite.cc](https://github.com/tile-ai/tilelang-ascend/blob/ascendc_pto/src/transform/ascend_storage_rewrite.cc#L1937) 读取 `tl.local_var_init`，并通过 [src/transfor'[:80]

