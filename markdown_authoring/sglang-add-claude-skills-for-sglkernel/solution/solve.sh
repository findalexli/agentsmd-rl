#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency guard
if grep -qF "tvm-ffi has optional headers to interop with parts of the C++ standard library (" ".claude/skills/add-jit-kernel/SKILL.md" && grep -qF "- If your underlying C++ API uses native types (e.g. `int`, `float`), but PyTorc" ".claude/skills/add-sgl-kernel/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-jit-kernel/SKILL.md b/.claude/skills/add-jit-kernel/SKILL.md
@@ -0,0 +1,276 @@
+---
+name: add-jit-kernel
+description: Step-by-step tutorial for adding a lightweight JIT CUDA/C++ kernel to python/sglang/jit_kernel (including tests & benchmarks)
+---
+
+# Tutorial: Adding a New Kernel to `python/sglang/jit_kernel` (JIT / Lightweight)
+
+This SKILL is a step-by-step guide for adding a **lightweight** CUDA/C++ kernel to `python/sglang/jit_kernel/`.
+
+Typical characteristics:
+
+- Few dependencies (usually tvm-ffi + a small subset of `sgl_kernel` utility headers)
+- Compiled at runtime (JIT), optimized for fast iteration
+- Avoids pulling heavyweight third-party/template code into AOT builds
+
+## Two rules of thumb (must follow)
+
+1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS / FlashInfer / DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.
+2. **Lightweight kernels go to `jit_kernel`.** If it is small and can be compiled independently, implement it here.
+
+## Stop and use `sgl-kernel` instead (important)
+
+Do **not** add a new kernel under `jit_kernel` if any of the following applies:
+
+- It directly depends on CUTLASS / FlashInfer (or other heavyweight third-party stacks)
+- It requires complex link-time integration, large template instantiations, or AOT-style packaging
+
+In addition, every new JIT kernel must ship with:
+
+- **Tests** (pytest)
+- **A benchmark script** (triton.testing)
+
+---
+
+## Goal
+
+Add a new JIT kernel end-to-end, including:
+
+- CUDA/C++ implementation in `jit_kernel/csrc`
+- A Python wrapper that compiles + loads the JIT module via tvm-ffi
+- Correctness tests
+- A reproducible benchmark (with CI-friendly ranges)
+
+---
+
+## Repository integration map
+
+You will typically touch these files/areas:
+
+- Implementation: `python/sglang/jit_kernel/csrc/`
+- Reusable headers: `python/sglang/jit_kernel/include/`
+- Python API: `python/sglang/jit_kernel/<op>.py`
+- JIT build + cache utilities: `python/sglang/jit_kernel/utils.py`
+- Tests: `python/sglang/jit_kernel/tests/test_<op>.py`
+- Benchmarks: `python/sglang/jit_kernel/benchmark/bench_<op>.py`
+- Benchmark helpers: `python/sglang/jit_kernel/benchmark/utils.py`
+
+---
+
+## tvm-ffi primer (practical, as used in this repo)
+
+This repository uses tvm-ffi primarily as a **stable C++ ABI** and a set of **lightweight container types** to move data between Python and C++ with minimal overhead.
+
+### Core types you will see in JIT kernels
+
+- `tvm::ffi::TensorView`
+  - A **non-owning view** of a tensor (backed by DLPack) that enables zero-copy interop.
+  - Use it for most tensor arguments in kernel entrypoints.
+  - You typically inspect/validate:
+    - Shape/strides: `dim()`, `shape()`, `strides()`, `size(i)`, `stride(i)`, `is_contiguous()`
+    - Dtype/device: `dtype()`, `device()`
+    - Raw pointer: `data_ptr()` (then cast after dtype checks)
+
+- `tvm::ffi::Optional<T>`
+  - Used for optional tensor arguments, e.g. `tvm::ffi::Optional<tvm::ffi::TensorView>`.
+  - Always check `has_value()` before using it.
+
+### Containers you may want (even if not widely used here yet)
+
+- `tvm::ffi::Array<T>`, `tvm::ffi::Tuple<...>`
+  - Useful for passing small structured metadata without inventing ad-hoc pointer conventions.
+
+### STL support
+
+tvm-ffi has optional headers to interop with parts of the C++ standard library (review mentions `extra/stl.h`). This repo currently mostly relies on `TensorView` + `Optional` for kernel interfaces.
+
+### Source of truth in `sglang`
+
+The most reliable documentation for how tvm-ffi is used in `sglang` is the code under:
+
+- `python/sglang/jit_kernel/include/`
+
+In particular:
+
+- `python/sglang/jit_kernel/include/sgl_kernel/tensor.h`
+  - `host::TensorMatcher` for validating shapes/strides/dtypes/devices
+  - Symbolic helper types used across many kernels:
+    - `host::SymbolicSize` / `host::SymbolicDType` / `host::SymbolicDevice`
+    - Typical pattern: declare symbols, validate with `TensorMatcher(...).verify(...)`, then `unwrap()` the resolved values for launch configuration
+
+---
+
+## Step 0 (optional): Generate a `.clangd` config for better IDE support
+
+Because JIT kernels compile at runtime, there is no static `compile_commands.json`.
+
+Run from your working directory (typically the repository root):
+
+```bash
+python -m sglang.jit_kernel
+```
+
+This will generate a `.clangd` file (and will not overwrite an existing one).
+
+---
+
+## Step 1: Implement the CUDA/C++ kernel in `jit_kernel/csrc/`
+
+1. Create a new source file:
+
+- `python/sglang/jit_kernel/csrc/<op>.cuh` (common pattern)
+
+2. Use the project’s recommended utilities.
+
+Notes:
+
+- Prefer reading and reusing the actual helper code in `python/sglang/jit_kernel/include/`.
+- If you find a missing helper that would be reusable across kernels, add it under `python/sglang/jit_kernel/include/`.
+
+- Use `tvm::ffi::TensorView` for tensor arguments (PyTorch tensors are passed through tvm-ffi)
+- Validate inputs with `TensorMatcher` (shape/stride/dtype/device)
+- Use `RuntimeCheck` / `RuntimeDeviceCheck` for readable runtime validation
+- Launch kernels via `LaunchKernel` (stream/device resolution)
+
+**Key points:**
+
+- Be explicit about contiguity/stride assumptions.
+- Make failures readable. A crash is not an error message.
+
+---
+
+## Step 2: Add the Python wrapper (compile + load with `load_jit`)
+
+Create:
+
+- `python/sglang/jit_kernel/<op>.py`
+
+### 2.1 Use `cache_once` for module caching
+
+Use `sglang.jit_kernel.utils.cache_once` (do **not** use `functools.lru_cache`).
+
+Reason: `functools.lru_cache` is not compatible with `torch.compile` in this codebase.
+
+### 2.2 Build and load the module with `load_jit`
+
+`load_jit` compiles a tvm-ffi module from C++/CUDA sources and returns a module object.
+
+Key fields:
+
+- `*args: str`: a unique marker for the build (different kernels / different template args must produce different markers)
+- `cpp_files` / `cuda_files`: filenames under `jit_kernel/csrc/`
+- `cpp_wrappers` / `cuda_wrappers`: list of `(export_name, kernel_symbol)`
+  - `export_name` is how you call it from Python: `module.export_name(...)`
+  - `kernel_symbol` is the C++ symbol name (can include template args)
+
+### 2.3 Template arguments (if needed)
+
+Use `make_cpp_args(...)` to convert Python values (int/float/bool/torch.dtype) into C++ template arguments.
+
+### 2.4 Destination-passing style (recommended)
+
+Prefer APIs that accept preallocated outputs (e.g. `out=` / `output=`) to avoid allocations in hot paths.
+
+---
+
+## Step 3 (optional): Tune JIT build flags
+
+`load_jit` supports:
+
+- `extra_cflags`, `extra_cuda_cflags`, `extra_ldflags`
+- `extra_include_paths`
+- `build_directory`
+
+**CUDA arch list:**
+
+`load_jit` sets `TVM_FFI_CUDA_ARCH_LIST` automatically if it is not already present.
+
+If your kernel has hard arch requirements (e.g. SM90+ only), enforce that:
+
+- In Python wrapper (raise a clear error)
+- In tests/benchmarks (skip or return NaN for unsupported providers)
+
+---
+
+## Step 4: Write tests (required)
+
+Create:
+
+- `python/sglang/jit_kernel/tests/test_<op>.py`
+
+**Recommended test patterns:**
+
+- Compare against a reference implementation (PyTorch or math definition)
+- If a corresponding op exists in `sgl-kernel` (AOT) or FlashInfer, add a cross-implementation equivalence test
+
+**Minimum coverage:**
+
+- Shapes: typical + edge cases
+- Dtypes: the dtypes you claim to support
+- Correctness: `torch.testing.assert_close` with appropriate tolerances
+- Failure modes: invalid dtype/shape/device should fail clearly (or be skipped)
+
+Run:
+
+```bash
+pytest python/sglang/jit_kernel/tests/test_<op>.py -q
+```
+
+---
+
+## Step 5: Add a benchmark (required)
+
+Create:
+
+- `python/sglang/jit_kernel/benchmark/bench_<op>.py`
+
+Use the shared helpers:
+
+- `python/sglang/jit_kernel/benchmark/utils.py`
+  - `is_in_ci()`
+  - `get_benchmark_range(...)`
+  - `run_benchmark(fn)` (uses `triton.testing.do_bench_cudagraph` and returns microseconds)
+
+**Minimum benchmark requirements:**
+
+- At least two providers/variants:
+  - Your JIT kernel
+  - A baseline (FlashInfer / `sgl-kernel` AOT / PyTorch / `torch.compile`)
+- CI-friendly reduced ranges (guard with `is_in_ci()` or env vars)
+- Use `triton.testing.Benchmark` + `triton.testing.perf_report`
+
+Run:
+
+```bash
+python python/sglang/jit_kernel/benchmark/bench_<op>.py
+```
+
+---
+
+## Troubleshooting
+
+- **JIT compilation fails**:
+  - Ensure the file is under `python/sglang/jit_kernel/csrc/`
+  - Reduce template argument combinations to minimize compilation scope
+
+- **CUDA crash / illegal memory access**:
+  - `CUDA_LAUNCH_BLOCKING=1`
+  - `compute-sanitizer --tool memcheck python ...`
+
+- **Unstable benchmark results**:
+  - Use CUDA-graph-based benchmarking (`run_benchmark` does this by default)
+  - Fix input distributions and shapes
+
+---
+
+## References
+
+- `docs/developer_guide/development_jit_kernel_guide.md`
+- `python/sglang/jit_kernel/utils.py` (`cache_once`, `load_jit`, wrappers, CUDA arch list)
+- `python/sglang/jit_kernel/include/sgl_kernel/tensor.h` (`TensorMatcher` and symbolic size/dtype/device helpers)
+- Existing kernels that are good references for utility usage:
+  - `python/sglang/jit_kernel/per_tensor_quant_fp8.py` + `python/sglang/jit_kernel/csrc/gemm/per_tensor_quant_fp8.cuh`
+  - `python/sglang/jit_kernel/norm.py` + `python/sglang/jit_kernel/csrc/elementwise/qknorm.cuh`
+  - `python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh`
+- `python/sglang/jit_kernel/tests/test_add_constant.py` (minimal runnable example)
+- `python/sglang/jit_kernel/benchmark/utils.py` (benchmark helpers)
diff --git a/.claude/skills/add-sgl-kernel/SKILL.md b/.claude/skills/add-sgl-kernel/SKILL.md
@@ -0,0 +1,217 @@
+---
+name: add-sgl-kernel
+description: Step-by-step tutorial for adding a heavyweight AOT CUDA/C++ kernel to sgl-kernel (including tests & benchmarks)
+---
+
+# Tutorial: Adding a New Kernel to `sgl-kernel` (AOT / Heavyweight)
+
+This SKILL is a step-by-step guide for adding a **heavyweight** CUDA/C++ kernel to `sgl-kernel/`.
+
+Typical characteristics:
+
+- Depends on heavyweight components such as CUTLASS / FlashInfer / DeepGEMM / sgl-attn
+- Needs AOT build and distribution (wheel / torch extension), so build time, link flags, CUDA arch targets, and binary size matter
+- Exposed as a stable `sgl_kernel` API and used by higher-level code (including `torch.compile`)
+
+## Two rules of thumb (must follow)
+
+1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS/FlashInfer/DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.
+2. **Lightweight kernels go to `python/sglang/jit_kernel`.** If it is small, has few dependencies, and benefits from rapid iteration, implement it as a JIT kernel instead.
+
+In addition, every new kernel must ship with:
+
+- **Tests** (pytest)
+- **A benchmark script** (triton.testing)
+
+---
+
+## Goal
+
+Add a new kernel end-to-end, including:
+
+- CUDA/C++ implementation
+- Torch library registration (`m.def` schema + `m.impl` dispatch)
+- Build system integration (CMake sources list)
+- Python-facing API
+- Correctness tests and performance benchmarks
+
+---
+
+## Repository integration map
+
+You will typically touch these files/areas:
+
+- Implementation: `sgl-kernel/csrc/...`
+- Public declarations: `sgl-kernel/include/sgl_kernel_ops.h`
+- Torch extension registration: `sgl-kernel/csrc/common_extension.cc`
+- Build: `sgl-kernel/CMakeLists.txt` (`set(SOURCES ...)`)
+- Python API: `sgl-kernel/python/sgl_kernel/...` and `sgl-kernel/python/sgl_kernel/__init__.py`
+- Tests: `sgl-kernel/tests/test_<op>.py`
+- Benchmarks: `sgl-kernel/benchmark/bench_<op>.py`
+
+---
+
+## Step 1: Implement the kernel in `csrc/`
+
+1. Pick the right subdirectory:
+
+- `csrc/elementwise/`
+- `csrc/gemm/`
+- `csrc/attention/`
+- `csrc/moe/`
+
+2. Implementation requirements:
+
+- Clearly define dtype/shape/stride/contiguity assumptions
+- If assumptions are violated, fail fast with a readable error (e.g. `TORCH_CHECK(...)`)
+- After kernel launch, perform device error checking (follow existing project conventions)
+
+**Key points:**
+
+- Prefer explicit validation over "it probably works".
+- If a kernel only works on certain architectures, make that restriction explicit (error/skip behavior).
+
+---
+
+## Step 2: Add a C++ declaration in `include/sgl_kernel_ops.h`
+
+Edit:
+
+- `sgl-kernel/include/sgl_kernel_ops.h`
+
+Add your function declaration in the appropriate section.
+
+---
+
+## Step 3: Register the op in `csrc/common_extension.cc` (schema + dispatch)
+
+Edit:
+
+- `sgl-kernel/csrc/common_extension.cc`
+
+Inside `TORCH_LIBRARY_FRAGMENT(sgl_kernel, m)`:
+
+1. Add `m.def(...)` with a **schema**.
+2. Add `m.impl(...)` for CUDA dispatch.
+
+**Key points:**
+
+- The schema is important for `torch.compile` and for consistent call signatures.
+- If your underlying C++ API uses native types (e.g. `int`, `float`), but PyTorch bindings expect `int64_t` / `double`, use the project’s recommended shim approach (see `sgl-kernel/README.md`).
+
+---
+
+## Step 4: Add the new source file to `CMakeLists.txt`
+
+Edit:
+
+- `sgl-kernel/CMakeLists.txt`
+
+Add your new `.cu` / `.cc` file to the `set(SOURCES ...)` list.
+
+**Key points:**
+
+- Keep the list **alphabetically sorted** (the file explicitly requires this).
+- If your kernel has arch constraints, reflect that in tests/benchmarks via skip logic.
+
+---
+
+## Step 5: Expose a Python API under `sgl-kernel/python/sgl_kernel/`
+
+Goal: users can call `sgl_kernel.<op>(...)`.
+
+- Add/extend a Python wrapper under `sgl-kernel/python/sgl_kernel/` (follow existing module organization).
+- Export it from `sgl-kernel/python/sgl_kernel/__init__.py`.
+
+---
+
+## Step 6: Write tests (required)
+
+Create:
+
+- `sgl-kernel/tests/test_<op>.py`
+
+**Minimum coverage:**
+
+- **Shapes**: typical + edge cases
+- **Dtypes**: whatever the kernel claims to support
+- **Correctness**: compare with a reference implementation (PyTorch / FlashInfer / another stable backend)
+- **Negative cases**: unsupported dtype/shape/arch should either raise a clear error or be explicitly skipped
+
+**Skipping by architecture:**
+
+- Use `@pytest.mark.skipif(..., reason="...")` when compute capability requirements apply.
+
+Run:
+
+```bash
+pytest sgl-kernel/tests/test_<op>.py -q
+```
+
+---
+
+## Step 7: Add a benchmark (required)
+
+Create:
+
+- `sgl-kernel/benchmark/bench_<op>.py`
+
+Follow the repository convention:
+
+- Use `triton.testing.Benchmark` + `triton.testing.perf_report`
+- Prefer `triton.testing.do_bench_cudagraph` for timing
+
+**Minimum benchmark requirements:**
+
+- At least two providers/variants:
+  - Your `sgl_kernel` implementation
+  - A baseline (PyTorch / `torch.compile` / Triton / FlashInfer)
+- Quantiles output (median/min/max)
+- CI-friendly ranges controlled by `CI` / `GITHUB_ACTIONS`
+
+Run:
+
+```bash
+python sgl-kernel/benchmark/bench_<op>.py
+```
+
+---
+
+## Step 8: Build and validate
+
+Build:
+
+```bash
+cd sgl-kernel
+make build -j16
+```
+
+If you need to limit host resource usage:
+
+```bash
+cd sgl-kernel
+make build -j1 MAX_JOBS=2 CMAKE_ARGS="-DSGL_KERNEL_COMPILE_THREADS=1"
+```
+
+Validate:
+
+- Tests: `pytest sgl-kernel/tests/test_<op>.py -q`
+- Benchmark: `python sgl-kernel/benchmark/bench_<op>.py`
+
+---
+
+## Troubleshooting
+
+- **Async CUDA errors**: `CUDA_LAUNCH_BLOCKING=1`
+- **Memory errors**: `compute-sanitizer --tool memcheck python ...`
+- **Build is too slow / OOM**: reduce `MAX_JOBS` and `SGL_KERNEL_COMPILE_THREADS`
+- **Binary bloat**: use `sgl-kernel/analyze_whl_kernel_sizes.py`
+
+---
+
+## References
+
+- `sgl-kernel/README.md`
+- `sgl-kernel/include/sgl_kernel_ops.h`
+- `sgl-kernel/csrc/common_extension.cc`
+- `sgl-kernel/CMakeLists.txt`
PATCH

echo "Gold patch applied."
