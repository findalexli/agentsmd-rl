"""Behavioral checks for flydsl-add-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flydsl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bisect-perf-regression/SKILL.md')
    assert 'User: /bisect-perf-regression v0.1.0 v0.2.0 -- python -m pytest tests/bench.py -k "test_throughput" --tb=no' in text, "expected to find: " + 'User: /bisect-perf-regression v0.1.0 v0.2.0 -- python -m pytest tests/bench.py -k "test_throughput" --tb=no'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bisect-perf-regression/SKILL.md')
    assert '| Refactored layout | Changed `BlockedLayout` params | Possible bank conflicts or non-coalesced access |' in text, "expected to find: " + '| Refactored layout | Changed `BlockedLayout` params | Possible bank conflicts or non-coalesced access |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/bisect-perf-regression/SKILL.md')
    assert '| JSON output `{"time": 1.23}` | `python3 -c "import json,sys; print(json.load(sys.stdin)[\'time\'])"` |' in text, "expected to find: " + '| JSON output `{"time": 1.23}` | `python3 -c "import json,sys; print(json.load(sys.stdin)[\'time\'])"` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-flydsl/SKILL.md')
    assert '| `[container@host]` | No | Target in format `container@hostname`. If omitted, build locally. Example: `hungry_dijkstra@hjbog-srdc-39.amd.com` |' in text, "expected to find: " + '| `[container@host]` | No | Target in format `container@hostname`. If omitted, build locally. Example: `hungry_dijkstra@hjbog-srdc-39.amd.com` |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-flydsl/SKILL.md')
    assert '| hungry_dijkstra | rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.8.0 | hjbog-srdc-39.amd.com | Verified 2026-03-10 |' in text, "expected to find: " + '| hungry_dijkstra | rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.8.0 | hjbog-srdc-39.amd.com | Verified 2026-03-10 |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-flydsl/SKILL.md')
    assert '- **`std::gcd not found` or redeclaration errors**: Wrong LLVM picked up. `unset MLIR_PATH` and let `build.sh` auto-detect.' in text, "expected to find: " + '- **`std::gcd not found` or redeclaration errors**: Wrong LLVM picked up. `unset MLIR_PATH` and let `build.sh` auto-detect.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-rocm-image/SKILL.md')
    assert 'description: Connect to a remote host via SSH and build a Docker image with rocprofv3, vllm, aiter, FlyDSL, and custom triton (rocm-maxnreg-support-v35 branch). Use when user wants to build/rebuild th' in text, "expected to find: " + 'description: Connect to a remote host via SSH and build a Docker image with rocprofv3, vllm, aiter, FlyDSL, and custom triton (rocm-maxnreg-support-v35 branch). Use when user wants to build/rebuild th'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-rocm-image/SKILL.md')
    assert 'When this skill is invoked, the argument passed in is the target hostname. Replace all occurrences of `<HOST>` below with the provided hostname. If no hostname is provided, ask the user for it before ' in text, "expected to find: " + 'When this skill is invoked, the argument passed in is the target hostname. Replace all occurrences of `<HOST>` below with the provided hostname. If no hostname is provided, ask the user for it before '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build-rocm-image/SKILL.md')
    assert 'LABEL description=\\"ROCm dev image with vllm(ROCm/ps_pa), aiter(main), FlyDSL(develop), rocprofv3, rocprof-trace-decoder, and custom triton (rocm-maxnreg-support-v35)\\"' in text, "expected to find: " + 'LABEL description=\\"ROCm dev image with vllm(ROCm/ps_pa), aiter(main), FlyDSL(develop), rocprofv3, rocprof-trace-decoder, and custom triton (rocm-maxnreg-support-v35)\\"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-flydsl-kernel/SKILL.md')
    assert "`gpu.barrier()` requires ALL threads in the workgroup to reach it. If some threads take a different branch (runtime `if`), the barrier deadlocks. FlyDSL doesn't support divergent barriers." in text, "expected to find: " + "`gpu.barrier()` requires ALL threads in the workgroup to reach it. If some threads take a different branch (runtime `if`), the barrier deadlocks. FlyDSL doesn't support divergent barriers."[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-flydsl-kernel/SKILL.md')
    assert 'For multi-partition kernels, verify the output is written to `part_z` slot (not absolute partition index). The reduce kernel reads from `part_z = 0..grid_z-1` slots.' in text, "expected to find: " + 'For multi-partition kernels, verify the output is written to `part_z` slot (not absolute partition index). The reduce kernel reads from `part_z = 0..grid_z-1` slots.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debug-flydsl-kernel/SKILL.md')
    assert '`buffer_ops.buffer_load(rsrc, offset, vec_width=4, dtype=T.i32)` — the offset is in units of `dtype`. For FP8 data addressed in bytes, divide by element size:' in text, "expected to find: " + '`buffer_ops.buffer_load(rsrc, offset, vec_width=4, dtype=T.i32)` — the offset is in units of `dtype`. For FP8 data addressed in bytes, divide by element size:'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flydsl-kernel-authoring/SKILL.md')
    assert 'FlyDSL is a Python DSL and MLIR-based compiler for writing high-performance GPU kernels on AMD GPUs (MI300X/MI350). It provides explicit layout algebra for controlling data movement, tiling, and memor' in text, "expected to find: " + 'FlyDSL is a Python DSL and MLIR-based compiler for writing high-performance GPU kernels on AMD GPUs (MI300X/MI350). It provides explicit layout algebra for controlling data movement, tiling, and memor'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flydsl-kernel-authoring/SKILL.md')
    assert '1. **Loop bounds must be `arith.index()`, NOT Python ints.** If you write `range(0, 15, 1, init=...)`, the AST rewriter treats constant bounds as a Python `range` and unrolls the loop — silently ignor' in text, "expected to find: " + '1. **Loop bounds must be `arith.index()`, NOT Python ints.** If you write `range(0, 15, 1, init=...)`, the AST rewriter treats constant bounds as a Python `range` and unrolls the loop — silently ignor'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flydsl-kernel-authoring/SKILL.md')
    assert '3. **Clear `SmemPtr._view_cache` before epilogue.** `SmemPtr.get()` caches the `memref.view` it creates. If called inside the `scf.for` body, the cached view is defined in the loop scope. Using it in ' in text, "expected to find: " + '3. **Clear `SmemPtr._view_cache` before epilogue.** `SmemPtr.get()` caches the `memref.view` it creates. If called inside the `scf.for` body, the cached view is defined in the loop scope. Using it in '[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/format-code/SKILL.md')
    assert 'Use this skill whenever the user says "format code", "clean up code", "lint", "format before commit",' in text, "expected to find: " + 'Use this skill whenever the user says "format code", "clean up code", "lint", "format before commit",'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/format-code/SKILL.md')
    assert '- This skill never adds or removes files from git staging -- it only modifies file contents in place.' in text, "expected to find: " + '- This skill never adds or removes files from git staging -- it only modifies file contents in place.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/format-code/SKILL.md')
    assert 'Check each tool and install any that are missing. Do all checks first, then install in one batch.' in text, "expected to find: " + 'Check each tool and install any that are missing. Do all checks first, then install in one batch.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gemm-optimization/SKILL.md')
    assert '| High `s_waitcnt vmcnt(0)` stall before MFMA | Global load latency exposed | Improve prefetch overlap, increase tile_k |' in text, "expected to find: " + '| High `s_waitcnt vmcnt(0)` stall before MFMA | Global load latency exposed | Improve prefetch overlap, increase tile_k |'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gemm-optimization/SKILL.md')
    assert '| High `s_waitcnt lgkmcnt(0)` stall | LDS latency exposed | Increase write-read distance, check bank conflicts |' in text, "expected to find: " + '| High `s_waitcnt lgkmcnt(0)` stall | LDS latency exposed | Increase write-read distance, check bank conflicts |'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/gemm-optimization/SKILL.md')
    assert '- B matrix is pre-shuffled to `(N/16, K/64, 4, 16, kpack_bytes)` layout — tile_k must divide K evenly' in text, "expected to find: " + '- B matrix is pre-shuffled to `(N/16, K/64, 4, 16, kpack_bytes)` layout — tile_k must divide K evenly'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lds-optimization/SKILL.md')
    assert '- **VGPR context**: LDS ops use **arch_vgpr** (not accum_vgpr). On CDNA3, arch_vgpr and accum_vgpr are separate 256-entry register files. LDS optimization does not interact with MFMA accumulator regis' in text, "expected to find: " + '- **VGPR context**: LDS ops use **arch_vgpr** (not accum_vgpr). On CDNA3, arch_vgpr and accum_vgpr are separate 256-entry register files. LDS optimization does not interact with MFMA accumulator regis'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lds-optimization/SKILL.md')
    assert '3. **Longer write-read distance = better latency hiding**: more instructions between `ds_write` and the subsequent `s_waitcnt lgkmcnt(0)` allow the write to complete in the background' in text, "expected to find: " + '3. **Longer write-read distance = better latency hiding**: more instructions between `ds_write` and the subsequent `s_waitcnt lgkmcnt(0)` allow the write to complete in the background'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lds-optimization/SKILL.md')
    assert "4. **Register pressure**: Swizzle adds ~1-2 SALU instructions for address XOR. Padding doesn't add register pressure but uses more LDS. Neither should significantly impact VGPR count." in text, "expected to find: " + "4. **Register pressure**: Swizzle adds ~1-2 SALU instructions for address XOR. Padding doesn't add register pressure but uses more LDS. Neither should significantly impact VGPR count."[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prefetch-data-load/SKILL.md')
    assert "- **Don't assume occupancy can increase**: on MI308 with 512 max VGPRs, adding prefetch buffers that push total VGPRs above 256 will drop occupancy from 2 to 1 wave/SIMD. This may or may not be accept" in text, "expected to find: " + "- **Don't assume occupancy can increase**: on MI308 with 512 max VGPRs, adding prefetch buffers that push total VGPRs above 256 will drop occupancy from 2 to 1 wave/SIMD. This may or may not be accept"[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prefetch-data-load/SKILL.md')
    assert "- **Don't prefetch too many buffers**: each prefetched variable occupies registers. If register pressure is already high (causing spills), prefetching more data makes it worse. Check `waves_per_eu` / " in text, "expected to find: " + "- **Don't prefetch too many buffers**: each prefetched variable occupies registers. If register pressure is already high (causing spills), prefetching more data makes it worse. Check `waves_per_eu` / "[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/prefetch-data-load/SKILL.md')
    assert "- **Don't reorder loads that have data dependencies**: if `load_B` depends on the result of `load_A` (e.g., block table lookup -> cache load), they must stay sequential within the prefetch block." in text, "expected to find: " + "- **Don't reorder loads that have data dependencies**: if `load_B` depends on the result of `load_A` (e.g., block table lookup -> cache load), they must stay sequential within the prefetch block."[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'FlyDSL (Flexible Layout Python DSL) — a Python DSL and MLIR-based compiler stack for authoring high-performance GPU kernels with explicit layouts and tiling on AMD GPUs (MI300X/MI350).' in text, "expected to find: " + 'FlyDSL (Flexible Layout Python DSL) — a Python DSL and MLIR-based compiler stack for authoring high-performance GPU kernels with explicit layouts and tiling on AMD GPUs (MI300X/MI350).'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Important: clear `SmemPtr._view_cache = None` after exiting scf.for to avoid MLIR dominance errors in epilogue code.' in text, "expected to find: " + 'Important: clear `SmemPtr._view_cache = None` after exiting scf.for to avoid MLIR dominance errors in epilogue code.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Always set `FLYDSL_RUNTIME_ENABLE_CACHE=0` when iterating on kernel code to bypass JIT cache' in text, "expected to find: " + '- Always set `FLYDSL_RUNTIME_ENABLE_CACHE=0` when iterating on kernel code to bypass JIT cache'[:80]

