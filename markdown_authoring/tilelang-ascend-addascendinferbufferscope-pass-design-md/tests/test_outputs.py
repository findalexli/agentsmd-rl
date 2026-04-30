"""Behavioral checks for tilelang-ascend-addascendinferbufferscope-pass-design-md (markdown_authoring task).

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
    text = _read('.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_infer_buffer_scope_design.md')
    assert '在 TileLang 前端，用户编写 Ascend 算子时使用统一的 `T.alloc_fragment` 与 `T.alloc_shared` 等抽象 API 申请片上 buffer。Ascend 后端代码生成阶段需要明确 buffer 落在哪一级物理存储上（L0A/L0B/L0C/L1/UB），否则 codegen 无法生成正确的搬运指令、寄存器声明和访问语义。`AscendInferBuff' in text, "expected to find: " + '在 TileLang 前端，用户编写 Ascend 算子时使用统一的 `T.alloc_fragment` 与 `T.alloc_shared` 等抽象 API 申请片上 buffer。Ascend 后端代码生成阶段需要明确 buffer 落在哪一级物理存储上（L0A/L0B/L0C/L1/UB），否则 codegen 无法生成正确的搬运指令、寄存器声明和访问语义。`AscendInferBuff'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_infer_buffer_scope_design.md')
    assert '某些 `shared.dyn` buffer 在 IR 中既不直接进入 GEMM，也不直接被 vector 算子使用，仅作为 `tl.ascend_copy` 的中间端点（典型场景：GM → buffer → L0A/L0B 的两段式搬运）。这时无法仅靠 `used_in_cube` / `used_in_vector` 推断 scope，需要观察对端：' in text, "expected to find: " + '某些 `shared.dyn` buffer 在 IR 中既不直接进入 GEMM，也不直接被 vector 算子使用，仅作为 `tl.ascend_copy` 的中间端点（典型场景：GM → buffer → L0A/L0B 的两段式搬运）。这时无法仅靠 `used_in_cube` / `used_in_vector` 推断 scope，需要观察对端：'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tilelang-pass-analyzer/references/pass-designs/ascend_infer_buffer_scope_design.md')
    assert '`gemm/mma/matmul` 类函数在 IR 中以 `call_extern("gemm_v0", access_ptr(A), access_ptr(B), access_ptr(C), ...)` 形式出现。本 pass 通过统计当前 `access_ptr` 之前的 `tvm_access_ptr` 数量来识别角色：' in text, "expected to find: " + '`gemm/mma/matmul` 类函数在 IR 中以 `call_extern("gemm_v0", access_ptr(A), access_ptr(B), access_ptr(C), ...)` 形式出现。本 pass 通过统计当前 `access_ptr` 之前的 `tvm_access_ptr` 数量来识别角色：'[:80]

