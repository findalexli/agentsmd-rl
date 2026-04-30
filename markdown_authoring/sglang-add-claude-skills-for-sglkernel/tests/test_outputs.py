"""Behavioral checks for sglang-add-claude-skills-for-sglkernel (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sglang")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-jit-kernel/SKILL.md')
    assert 'tvm-ffi has optional headers to interop with parts of the C++ standard library (review mentions `extra/stl.h`). This repo currently mostly relies on `TensorView` + `Optional` for kernel interfaces.' in text, "expected to find: " + 'tvm-ffi has optional headers to interop with parts of the C++ standard library (review mentions `extra/stl.h`). This repo currently mostly relies on `TensorView` + `Optional` for kernel interfaces.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-jit-kernel/SKILL.md')
    assert 'This repository uses tvm-ffi primarily as a **stable C++ ABI** and a set of **lightweight container types** to move data between Python and C++ with minimal overhead.' in text, "expected to find: " + 'This repository uses tvm-ffi primarily as a **stable C++ ABI** and a set of **lightweight container types** to move data between Python and C++ with minimal overhead.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-jit-kernel/SKILL.md')
    assert '1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS / FlashInfer / DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.' in text, "expected to find: " + '1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS / FlashInfer / DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-sgl-kernel/SKILL.md')
    assert '- If your underlying C++ API uses native types (e.g. `int`, `float`), but PyTorch bindings expect `int64_t` / `double`, use the project’s recommended shim approach (see `sgl-kernel/README.md`).' in text, "expected to find: " + '- If your underlying C++ API uses native types (e.g. `int`, `float`), but PyTorch bindings expect `int64_t` / `double`, use the project’s recommended shim approach (see `sgl-kernel/README.md`).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-sgl-kernel/SKILL.md')
    assert '2. **Lightweight kernels go to `python/sglang/jit_kernel`.** If it is small, has few dependencies, and benefits from rapid iteration, implement it as a JIT kernel instead.' in text, "expected to find: " + '2. **Lightweight kernels go to `python/sglang/jit_kernel`.** If it is small, has few dependencies, and benefits from rapid iteration, implement it as a JIT kernel instead.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-sgl-kernel/SKILL.md')
    assert '1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS/FlashInfer/DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.' in text, "expected to find: " + '1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS/FlashInfer/DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.'[:80]

