# Agent Config Files for sglang-flux2-tokenization-length

Repo: sgl-project/sglang
Commit: edd4d540237be4267c3a260d6a2f23a035e203af
Files found: 24


---
## .claude/skills/add-jit-kernel/SKILL.md

```
   1 | ---
   2 | name: add-jit-kernel
   3 | description: Step-by-step tutorial for adding a new lightweight JIT CUDA kernel to sglang's jit_kernel module
   4 | ---
   5 | 
   6 | # Tutorial: Adding a New JIT Kernel to SGLang
   7 | 
   8 | This tutorial walks through adding a simple element-wise scale operation as a JIT kernel. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.
   9 | 
  10 | ## Goal
  11 | 
  12 | Add a new operation that scales each element of a tensor by a scalar factor:
  13 | 
  14 | - Input: tensor `x` (CUDA) and scalar `factor` (float, passed at runtime)
  15 | - Output: `x * factor` (element-wise), allocated internally
  16 | - Supported dtypes: **FP16 (`torch.float16`), BF16 (`torch.bfloat16`), FP32 (`torch.float32`)**
  17 | 
  18 | ## When to use JIT vs AOT (`sgl-kernel`)
  19 | 
  20 | - **JIT (`jit_kernel`)**: prefer this first for kernels that do **not** depend on CUTLASS or another large C++ project. It is the default choice for lightweight kernels that benefit from rapid iteration and first-use compilation.
  21 | - **AOT (`sgl-kernel`)**: prefer this when the kernel **does** depend on CUTLASS or another large C++ project, or when it should live in `sgl-kernel/` and participate in the wheel build / torch op registration flow.
  22 | - **Exception**: kernels that depend on `flashinfer`, or on CUTLASS that is already provided through `flashinfer`, can still be implemented as `jit_kernel`.
  23 | 
  24 | ---
  25 | 
  26 | ## Common Abstractions in `python/sglang/jit_kernel/include/sgl_kernel/`
  27 | 
  28 | **Always prefer these abstractions over raw CUDA primitives.** They provide safety, readability, and consistency with the rest of the codebase.
  29 | 
  30 | **Important include rule:** for every `#include <sgl_kernel/...>` line, add a short trailing comment explaining why that header is included (for example `// For TensorMatcher, SymbolicSize, SymbolicDevice`). This matches the current JIT kernel style and keeps include usage self-documenting.
  31 | 
  32 | ### `utils.h` — Host-side utilities
  33 | 
  34 | ```cpp
  35 | #include <sgl_kernel/utils.h>
  36 | ```
  37 | 
  38 | - **`host::RuntimeCheck(cond, args...)`** — Assert a condition at runtime; throws `PanicError` with file/line info on failure. Prefer this over bare `assert`.
  39 | - **`host::Panic(args...)`** — Unconditionally throw a `PanicError` with a descriptive message.
  40 | - **`host::div_ceil(a, b)`** — Integer ceiling division `(a + b - 1) / b`.
  41 | - **`host::irange(n)`** / **`host::irange(start, end)`** — Range views for cleaner loops.
  42 | - **`host::pointer::offset(ptr, offsets...)`** — Byte-safe pointer arithmetic on `void*`. Use this instead of raw casts.
  43 | 
  44 | ### `utils.cuh` — Device-side utilities + `LaunchKernel`
  45 | 
  46 | ```cpp
  47 | #include <sgl_kernel/utils.cuh>
  48 | ```
  49 | 
  50 | - **Type aliases**: `fp16_t`, `bf16_t`, `fp32_t`, `fp8_e4m3_t`, `fp8_e5m2_t` and their packed variants `fp16x2_t`, `bf16x2_t`, `fp32x2_t`, etc.
  51 | - **`SGL_DEVICE`** — Expands to `__forceinline__ __device__`. Use on all device functions.
  52 | - **`device::kWarpThreads`** — Constant `32`.
  53 | - **`device::load_as<T>(ptr, offset)`** / **`device::store_as<T>(ptr, val, offset)`** — Type-safe loads/stores from `void*`.
  54 | - **`device::pointer::offset(ptr, offsets...)`** — Pointer arithmetic on device.
  55 | - **`host::LaunchKernel(grid, block, device_or_stream [, smem])`** — RAII kernel launcher that:
  56 |   - Resolves the CUDA stream from a `DLDevice` via TVM-FFI automatically.
  57 |   - Checks the CUDA error with file/line info after launch via `operator()(kernel, args...)`.
  58 |   - Supports `.enable_pdl(bool)` for PDL (Programmatic Dependent Launch, SM90+).
  59 | - **`host::RuntimeDeviceCheck(cudaError_t)`** — Check a CUDA error; throw on failure.
  60 | 
  61 | ### `tensor.h` — Tensor validation (`TensorMatcher`, Symbolic types)
  62 | 
  63 | ```cpp
  64 | #include <sgl_kernel/tensor.h>
  65 | ```
  66 | 
  67 | This is the **primary validation API** for all kernel launchers. Use it to validate every `tvm::ffi::TensorView` argument.
  68 | 
  69 | - **`host::SymbolicSize{"name"}`** — A named symbolic dimension. Call `.set_value(n)` to pin it, `.unwrap()` to extract after verification.
  70 | - **`host::SymbolicDType`** — Symbolic dtype. Use `.set_options<Ts...>()` to restrict allowed types.
  71 | - **`host::SymbolicDevice`** — Symbolic device. Use `.set_options<kDLCUDA>()` to restrict to CUDA.
  72 | - **`host::TensorMatcher({dims...})`** — Fluent builder for tensor validation:
  73 |   - `.with_dtype<T>()` — require a specific C++ type (e.g. `fp16_t`)
  74 |   - `.with_dtype<T1, T2, ...>()` — allow a set of types
  75 |   - `.with_device<kDLCUDA>(device_sym)` — require CUDA and bind the checked device to a `SymbolicDevice`
  76 |   - `.with_strides({strides...})` — validate strides (omit to require contiguous)
  77 |   - `.verify(tensor_view)` — execute the check; throws `PanicError` with full context on failure; **chainable** (`verify(a).verify(b)` to check multiple tensors with the same shape)
  78 | 
  79 | **Typical pattern:**
  80 | ```cpp
  81 | auto N = SymbolicSize{"num_elements"};
  82 | auto device = SymbolicDevice{};
  83 | device.set_options<kDLCUDA>();
  84 | TensorMatcher({N})  //
  85 |     .with_dtype<fp16_t>()
  86 |     .with_device<kDLCUDA>(device)
  87 |     .verify(dst)
  88 |     .verify(src);  // same shape, dtype, device as dst
  89 | const size_t n = N.unwrap();
  90 | const DLDevice dev = device.unwrap();
  91 | ```
  92 | 
  93 | ### `type.cuh` — `dtype_trait<T>` and `packed_t<T>`
  94 | 
  95 | ```cpp
  96 | #include <sgl_kernel/type.cuh>
  97 | ```
  98 | 
  99 | - **`dtype_trait<T>`** — Static trait struct for each scalar type. Provides:
 100 |   - `dtype_trait<T>::from(value)` — convert from another type (e.g. `fp32_t` → `fp16_t`)
 101 |   - `dtype_trait<T>::abs/sqrt/rsqrt/exp/sin/cos(x)` — type-dispatched unary math (primarily for `fp32_t`)
 102 |   - `dtype_trait<T>::max/min(x, y)` — type-dispatched binary math (primarily for `fp32_t`)
 103 | - **`packed_t<T>`** — Two-element packed alias: `packed_t<fp16_t>` = `fp16x2_t`, `packed_t<bf16_t>` = `bf16x2_t`, `packed_t<fp32_t>` = `fp32x2_t`. Use for vectorized loads/stores.
 104 | - **`device::cast<To, From>(value)`** — Type-safe cast using `dtype_trait`, e.g. `cast<fp32x2_t, fp16x2_t>(v)`.
 105 | 
 106 | ### `vec.cuh` — Vectorized memory access (`AlignedVector`)
 107 | 
 108 | ```cpp
 109 | #include <sgl_kernel/vec.cuh>
 110 | ```
 111 | 
 112 | - **`device::AlignedVector<T, N>`** — Aligned storage for N elements of type T. N must be a power of two, `sizeof(T)*N <= 32`. Enables vectorized loads/stores for bandwidth efficiency. In terms of API/codegen constraints, the upper bound is 256-bit; in practice, 128-bit is the portable default, while 256-bit vectorization is typically only viable on `SM100+` and should be gated by an architecture check when needed.
 113 |   - `.load(ptr, offset)` — vectorized load from `ptr[offset]`
 114 |   - `.store(ptr, offset)` — vectorized store to `ptr[offset]`
 115 |   - `.fill(value)` — fill all lanes
 116 |   - `operator[](i)` — element access
 117 | 
 118 | ### `tile.cuh` — `tile::Memory` (strided memory access pattern)
 119 | 
 120 | ```cpp
 121 | #include <sgl_kernel/tile.cuh>
 122 | ```
 123 | 
 124 | - `tile::Memory<T>` is fundamentally a **1D cooperative accessor** over a contiguous region.
 125 | - **`device::tile::Memory<T>::cta(blockDim.x)`** — Creates a tile accessor where each thread handles `tid = threadIdx.x` with stride `tsize` (for `cta(blockDim.x)`, this is `blockDim.x`). Common for loops over a 1D array.
 126 | - **`.load(ptr, offset)`** — loads `ptr[tid + offset * tsize]`
 127 | - **`.store(ptr, val, offset)`** — stores to `ptr[tid + offset * tsize]`
 128 | - **`.in_bound(n, offset)`** — boundary check
 129 | 
 130 | For a **2D tile**, either flatten `(row, col)` into a linear tile index first, or compute the address manually with `ptr[row * stride + col]` using your thread/block coordinates.
 131 | 
 132 | ### `math.cuh` — Device math (`device::math::`)
 133 | 
 134 | ```cpp
 135 | #include <sgl_kernel/math.cuh>
 136 | ```
 137 | 
 138 | - `device::math::max/min<T>(a, b)` — type-dispatched binary math via `dtype_trait`
 139 | - `device::math::abs/sqrt/rsqrt/exp/sin/cos<T>(x)` — type-dispatched unary math via `dtype_trait`
 140 | 
 141 | ### `warp.cuh` — Warp-level primitives
 142 | 
 143 | ```cpp
 144 | #include <sgl_kernel/warp.cuh>
 145 | ```
 146 | 
 147 | - `device::warp::reduce_sum<T>(value)` — warp-level sum reduction via `__shfl_xor_sync`
 148 | - `device::warp::reduce_max<T>(value)` — warp-level max reduction
 149 | 
 150 | ### `cta.cuh` — CTA-level primitives
 151 | 
 152 | ```cpp
 153 | #include <sgl_kernel/cta.cuh>
 154 | ```
 155 | 
 156 | - `device::cta::reduce_max<T>(value, smem, min_value)` — CTA-wide max using shared memory + warp reduction. Caller is responsible for a `__syncthreads()` after if the result in `smem[0]` is needed.
 157 | 
 158 | ### `atomic.cuh` — Atomic operations
 159 | 
 160 | ```cpp
 161 | #include <sgl_kernel/atomic.cuh>
 162 | ```
 163 | 
 164 | - `device::atomic::max(float* addr, float value)` — float atomic max (handles negative values correctly via bit tricks).
 165 | 
 166 | ### `runtime.cuh` — Occupancy and device info
 167 | 
 168 | ```cpp
 169 | #include <sgl_kernel/runtime.cuh>
 170 | ```
 171 | 
 172 | - `host::runtime::get_blocks_per_sm(kernel, block_dim)` — max active blocks per SM (occupancy)
 173 | - `host::runtime::get_sm_count(device_id)` — number of SMs on the device
 174 | - `host::runtime::get_cc_major(device_id)` — compute capability major version
 175 | 
 176 | **Persistent kernel pattern** (cap blocks to SM count × occupancy):
 177 | ```cpp
 178 | static const uint32_t max_occ = runtime::get_blocks_per_sm(kernel, kBlockSize);
 179 | static const uint32_t num_sm  = runtime::get_sm_count(device.unwrap().device_id);
 180 | const auto num_blocks = std::min(num_sm * max_occ, div_ceil(n, kBlockSize));
 181 | LaunchKernel(num_blocks, kBlockSize, device.unwrap())(kernel, params);
 182 | ```
 183 | 
 184 | ---
 185 | 
 186 | ## Step 0 (optional): Generate a `.clangd` config for better IDE support
 187 | 
 188 | ```bash
 189 | python -m sglang.jit_kernel
 190 | ```
 191 | 
 192 | ---
 193 | 
 194 | ## Step 1: Implement the CUDA kernel in `jit_kernel/csrc/`
 195 | 
 196 | Create `python/sglang/jit_kernel/csrc/elementwise/scale.cuh`.
 197 | 
 198 | The implementation fully uses the project abstractions described above:
 199 | 
 200 | ```cpp
 201 | #include <sgl_kernel/tensor.h>   // For TensorMatcher, SymbolicSize, SymbolicDevice
 202 | #include <sgl_kernel/type.cuh>   // For dtype_trait, fp16_t, bf16_t, fp32_t
 203 | #include <sgl_kernel/utils.h>    // For RuntimeCheck, div_ceil
 204 | #include <sgl_kernel/utils.cuh>  // For LaunchKernel, SGL_DEVICE
 205 | #include <sgl_kernel/vec.cuh>    // For AlignedVector
 206 | 
 207 | #include <dlpack/dlpack.h>
 208 | #include <tvm/ffi/container/tensor.h>
 209 | 
 210 | namespace {
 211 | 
 212 | // ----------------------------------------------------------------
 213 | // Kernel: element-wise scale using vectorized 128-bit loads/stores
 214 | // T       = fp16_t | bf16_t | fp32_t
 215 | // kVecN   = number of elements per vector load (e.g. 8 for fp16)
 216 | // factor  = runtime scale factor
 217 | // ----------------------------------------------------------------
 218 | template <typename T, int kVecN>
 219 | __global__ void scale_kernel(T* __restrict__ dst,
 220 |                               const T* __restrict__ src,
 221 |                               float factor,
 222 |                               uint32_t n_total) {
 223 |   using vec_t = device::AlignedVector<T, kVecN>;
 224 |   const uint32_t n_vecs = n_total / kVecN;
 225 | 
 226 |   // --- vectorised body ---
 227 |   const uint32_t vec_stride = blockDim.x * gridDim.x;
 228 |   for (uint32_t vi = blockIdx.x * blockDim.x + threadIdx.x;
 229 |        vi < n_vecs;
 230 |        vi += vec_stride) {
 231 |     vec_t v;
 232 |     v.load(src, vi);
 233 | #pragma unroll
 234 |     for (int i = 0; i < kVecN; ++i) {
 235 |       v[i] = static_cast<T>(static_cast<float>(v[i]) * factor);
 236 |     }
 237 |     v.store(dst, vi);
 238 |   }
 239 | 
 240 |   // --- scalar tail ---
 241 |   const uint32_t base = n_vecs * kVecN;
 242 |   const uint32_t scalar_stride = blockDim.x * gridDim.x;
 243 |   for (uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
 244 |        base + i < n_total;
 245 |        i += scalar_stride) {
 246 |     dst[base + i] = static_cast<T>(static_cast<float>(src[base + i]) * factor);
 247 |   }
 248 | }
 249 | 
 250 | // ----------------------------------------------------------------
 251 | // Launcher: validates tensors, selects vector width, launches kernel
 252 | // ----------------------------------------------------------------
 253 | template <typename T>
 254 | void scale(tvm::ffi::TensorView dst, tvm::ffi::TensorView src, float factor) {
 255 |   using namespace host;
 256 | 
 257 |   // 1. Validate input tensors with TensorMatcher
 258 |   SymbolicSize N = {"num_elements"};
 259 |   SymbolicDevice device_;
 260 |   device_.set_options<kDLCUDA>();
 261 | 
 262 |   TensorMatcher({N})  //
 263 |       .with_dtype<T>()
 264 |       .with_device<kDLCUDA>(device_)
 265 |       .verify(dst)
 266 |       .verify(src);  // same shape / dtype / device as dst
 267 | 
 268 |   const uint32_t n = static_cast<uint32_t>(N.unwrap());
 269 |   const DLDevice device = device_.unwrap();
 270 | 
 271 |   RuntimeCheck(n > 0, "scale: num_elements must be > 0, got ", n);
 272 | 
 273 |   // 2. Choose vector width for 128-bit loads (16 bytes)
 274 |   //    fp16/bf16: 8 elements × 2 bytes = 16 bytes
 275 |   //    fp32:      4 elements × 4 bytes = 16 bytes
 276 |   constexpr int kVecN = 16 / sizeof(T);
 277 |   const uint32_t n_work_items = div_ceil(n, static_cast<uint32_t>(kVecN));
 278 | 
 279 |   // 3. Launch
 280 |   constexpr uint32_t kBlockSize = 256;
 281 |   const uint32_t grid = div_ceil(n_work_items, kBlockSize);
 282 | 
 283 |   LaunchKernel(grid, kBlockSize, device)(
 284 |       scale_kernel<T, kVecN>,
 285 |       static_cast<T*>(dst.data_ptr()),
 286 |       static_cast<const T*>(src.data_ptr()),
 287 |       factor,
 288 |       n);
 289 | }
 290 | 
 291 | }  // namespace
 292 | ```
 293 | 
 294 | **Key points:**
 295 | 
 296 | - Include headers from `sgl_kernel/` — **not** raw CUDA headers for anything already covered
 297 | - Add a short trailing `// For ...` explanation to every `#include <sgl_kernel/...>` line
 298 | - Use `TensorMatcher` for all tensor validation; never manually check shape/dtype/device
 299 | - Use `AlignedVector` for vectorised 128-bit loads/stores — significant bandwidth win
 300 | - Use `LaunchKernel` — it resolves the stream and checks errors automatically
 301 | - Use `RuntimeCheck` for runtime assertions with useful error messages
 302 | - Prefer passing runtime scalars like `factor` directly unless compile-time specialisation is genuinely required
 303 | - `fp16_t` / `bf16_t` / `fp32_t` are the project's type aliases (from `utils.cuh`)
 304 | - `device::cast<To, From>` or `dtype_trait<T>::from(val)` for cross-type conversions
 305 | - `device::math::` functions for device math instead of bare `__` intrinsics
 306 | 
 307 | ---
 308 | 
 309 | ## Step 2: Add the Python wrapper in `jit_kernel/`
 310 | 
 311 | Create `python/sglang/jit_kernel/scale.py`:
 312 | 
 313 | ```python
 314 | from __future__ import annotations
 315 | 
 316 | from typing import TYPE_CHECKING
 317 | 
 318 | import torch
 319 | 
 320 | from sglang.jit_kernel.utils import cache_once, load_jit, make_cpp_args
 321 | 
 322 | if TYPE_CHECKING:
 323 |     from tvm_ffi.module import Module
 324 | 
 325 | 
 326 | @cache_once
 327 | def _jit_scale_module(dtype: torch.dtype) -> Module:
 328 |     """Compile and cache the JIT scale module for a given dtype."""
 329 |     args = make_cpp_args(dtype)
 330 |     return load_jit(
 331 |         "scale",
 332 |         *args,
 333 |         cuda_files=["elementwise/scale.cuh"],
 334 |         cuda_wrappers=[("scale", f"scale<{args}>")],
 335 |     )
 336 | 
 337 | 
 338 | def scale(src: torch.Tensor, factor: float, out: torch.Tensor | None = None) -> torch.Tensor:
 339 |     """
 340 |     Element-wise scale: dst = src * factor.
 341 | 
 342 |     Supported dtypes: torch.float16, torch.bfloat16, torch.float32.
 343 | 
 344 |     Parameters
 345 |     ----------
 346 |     src    : CUDA tensor (FP16 / BF16 / FP32)
 347 |     factor : scale factor
 348 |     out    : optional pre-allocated output tensor (same shape/dtype as src)
 349 | 
 350 |     Returns
 351 |     -------
 352 |     Scaled tensor (dst = src * factor).
 353 |     """
 354 |     if not src.is_cuda:
 355 |         raise RuntimeError("src must be a CUDA tensor")
 356 |     if src.dtype not in (torch.float16, torch.bfloat16, torch.float32):
 357 |         raise RuntimeError(
 358 |             f"Unsupported dtype {src.dtype}. Supported: float16, bfloat16, float32"
 359 |         )
 360 |     if out is None:
 361 |         out = torch.empty_like(src)
 362 |     else:
 363 |         if out.shape != src.shape:
 364 |             raise RuntimeError("out shape must match src")
 365 |         if out.dtype != src.dtype:
 366 |             raise RuntimeError("out dtype must match src")
 367 |         if out.device != src.device:
 368 |             raise RuntimeError("out device must match src")
 369 | 
 370 |     # Keep the Python wrapper thin, but still enforce the basic preconditions
 371 |     # that the current JIT/FFI path does not reject safely on its own.
 372 |     module = _jit_scale_module(src.dtype)
 373 |     module.scale(out, src, factor)
 374 |     return out
 375 | ```
 376 | 
 377 | **Key points:**
 378 | 
 379 | - Use `cache_once` — **not** `functools.lru_cache` (incompatible with `torch.compile`)
 380 | - `load_jit` first arg(s) form the unique build marker; same marker = same cached binary
 381 | - Only include compile-time specialisation knobs in the build marker; runtime values like `factor` should stay runtime unless the kernel truly needs templating
 382 | - `cuda_wrappers`: `(export_name, kernel_symbol)` — `export_name` is called from Python
 383 | - `make_cpp_args(dtype, ...)` converts `torch.dtype` to C++ type alias:
 384 | - Keep Python launchers thin, but still validate the basic invariants (`is_cuda`, supported dtype, `out` metadata). In the current JIT/FFI path, invalid tensors are not always rejected safely before launch
 385 | 
 386 | | `torch.dtype`      | C++ type   |
 387 | |--------------------|------------|
 388 | | `torch.float16`    | `fp16_t`   |
 389 | | `torch.bfloat16`   | `bf16_t`   |
 390 | | `torch.float32`    | `fp32_t`   |
 391 | 
 392 | ---
 393 | 
 394 | ## Step 3 (optional): Tune JIT build flags
 395 | 
 396 | ```python
 397 | return load_jit(
 398 |     "scale",
 399 |     *args,
 400 |     cuda_files=["elementwise/scale.cuh"],
 401 |     cuda_wrappers=[("scale", f"scale<{args}>")],
 402 |     extra_cuda_cflags=["-O3", "--use_fast_math"],
 403 | )
 404 | ```
 405 | 
 406 | If your kernel requires SM90+, raise a clear Python error before calling `load_jit`:
 407 | 
 408 | ```python
 409 | if torch.cuda.get_device_capability()[0] < 9:
 410 |     raise RuntimeError("This kernel requires SM90 (Hopper) or later")
 411 | ```
 412 | 
 413 | ---
 414 | 
 415 | ## Step 4: Write tests (required)
 416 | 
 417 | JIT kernel tests live under `python/sglang/jit_kernel/tests/`. **CI does not run `pytest` in that directory directly.** The unified runner `test/run_suite.py` discovers every `test_*.py` there (and every `bench_*.py` under `benchmark/`), collects `register_*_ci(...)` calls by **statically parsing each file’s AST**, and executes the selected suite. Every test file must register at least one CUDA entry or the collector fails its sanity check.
 418 | 
 419 | - **PR / per-commit CUDA suites** (see `test/run_suite.py` → `PER_COMMIT_SUITES`): JIT unit tests use `stage-b-kernel-unit-1-gpu-large` (see `.github/workflows/pr-test-jit-kernel.yml`: `python3 run_suite.py --hw cuda --suite stage-b-kernel-unit-1-gpu-large`).
 420 | - **Nightly kernel suite**: `nightly-kernel-1-gpu` with `--nightly` — typically used with `SGLANG_JIT_KERNEL_RUN_FULL_TESTS=1` in CI for expanded parameter grids (see `python/sglang/jit_kernel/utils.py` → `should_run_full_tests` / `get_ci_test_range`). Wired in `.github/workflows/nightly-test-nvidia.yml` (e.g. `python3 run_suite.py --hw cuda --suite nightly-kernel-1-gpu --nightly --continue-on-error`).
 421 | 
 422 | Registration pattern (module level, **literal** `est_time` and `suite` strings — required for AST parsing):
 423 | 
 424 | ```python
 425 | from sglang.test.ci.ci_register import register_cuda_ci
 426 | 
 427 | register_cuda_ci(est_time=30, suite="stage-b-kernel-unit-1-gpu-large")
 428 | # Optional second registration: same file also listed under the nightly kernel suite
 429 | # register_cuda_ci(est_time=120, suite="nightly-kernel-1-gpu", nightly=True)
 430 | ```
 431 | 
 432 | Keep `est_time` and `suite` as literal values. `run_suite.py` collects them from the file AST, so computed values and helper wrappers can break CI discovery.
 433 | 
 434 | Use `register_cuda_ci(..., disabled="reason")` if the file must stay in-tree but should be skipped in CI (e.g. multi-GPU only).
 435 | 
 436 | **Run like CI** (from repo root):
 437 | 
 438 | ```bash
 439 | cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-unit-1-gpu-large
 440 | ```
 441 | 
 442 | For fast iteration you can still run `pytest` on a single file locally; CI coverage is via `run_suite.py`.
 443 | 
 444 | Create `python/sglang/jit_kernel/tests/test_scale.py`:
 445 | 
 446 | ```python
 447 | import pytest
 448 | import torch
 449 | from sglang.jit_kernel.scale import scale
 450 | from sglang.test.ci.ci_register import register_cuda_ci
 451 | 
 452 | register_cuda_ci(est_time=30, suite="stage-b-kernel-unit-1-gpu-large")
 453 | 
 454 | 
 455 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 456 | @pytest.mark.parametrize("size", [1, 127, 128, 1024, 4097])  # cover tail remainder
 457 | @pytest.mark.parametrize("factor", [0.5, 1.0, 2.0, 3.0])
 458 | def test_scale_correctness(dtype, size, factor):
 459 |     src = torch.randn(size, dtype=dtype, device="cuda")
 460 |     out = scale(src, factor)
 461 |     expected = src * factor
 462 | 
 463 |     rtol, atol = (1e-5, 1e-6) if dtype == torch.float32 else (1e-2, 1e-2)
 464 |     torch.testing.assert_close(out, expected, rtol=rtol, atol=atol)
 465 | 
 466 | 
 467 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 468 | def test_scale_out_param(dtype):
 469 |     src = torch.randn(1024, dtype=dtype, device="cuda")
 470 |     out = torch.empty_like(src)
 471 |     result = scale(src, 2.0, out=out)
 472 |     assert result is out
 473 |     torch.testing.assert_close(out, src * 2.0, rtol=1e-2, atol=1e-2)
 474 | 
 475 | 
 476 | def test_scale_cpu_error():
 477 |     src = torch.randn(128, dtype=torch.float16)  # CPU tensor
 478 |     with pytest.raises(RuntimeError, match="CUDA"):
 479 |         scale(src, 2.0)
 480 | 
 481 | 
 482 | def test_scale_unsupported_dtype():
 483 |     src = torch.randint(0, 10, (128,), dtype=torch.int32, device="cuda")
 484 |     with pytest.raises(RuntimeError, match="dtype"):
 485 |         scale(src, 2.0)
 486 | 
 487 | 
 488 | if __name__ == "__main__":
 489 |     import sys
 490 |     sys.exit(pytest.main([__file__, "-v", "-s"]))
 491 | ```
 492 | 
 493 | ---
 494 | 
 495 | ## Step 5: Add a benchmark (required)
 496 | 
 497 | Benchmarks are `bench_*.py` files under `python/sglang/jit_kernel/benchmark/`. They are picked up by the same `run_suite.py` machinery as unit tests. Register them for **`stage-b-kernel-benchmark-1-gpu-large`** (PR JIT benchmark job: `python3 run_suite.py --hw cuda --suite stage-b-kernel-benchmark-1-gpu-large`).
 498 | 
 499 | Create `python/sglang/jit_kernel/benchmark/bench_scale.py`:
 500 | 
 501 | ```python
 502 | import itertools
 503 | 
 504 | import torch
 505 | import triton
 506 | import triton.testing
 507 | 
 508 | from sglang.jit_kernel.benchmark.utils import (
 509 |     DEFAULT_DEVICE,
 510 |     DEFAULT_DTYPE,
 511 |     get_benchmark_range,
 512 |     run_benchmark,
 513 | )
 514 | from sglang.jit_kernel.scale import scale as jit_scale
 515 | from sglang.test.ci.ci_register import register_cuda_ci
 516 | 
 517 | register_cuda_ci(est_time=6, suite="stage-b-kernel-benchmark-1-gpu-large")
 518 | 
 519 | SIZE_LIST = get_benchmark_range(
 520 |     full_range=[2**n for n in range(10, 20)],  # 1K … 512K elements
 521 |     ci_range=[4096, 65536],
 522 | )
 523 | 
 524 | configs = list(itertools.product(SIZE_LIST))
 525 | 
 526 | 
 527 | @triton.testing.perf_report(
 528 |     triton.testing.Benchmark(
 529 |         x_names=["size"],
 530 |         x_vals=configs,
 531 |         line_arg="provider",
 532 |         line_vals=["jit", "torch"],
 533 |         line_names=["SGL JIT Kernel", "PyTorch"],
 534 |         styles=[("blue", "-"), ("red", "--")],
 535 |         ylabel="us",
 536 |         plot_name="scale-performance",
 537 |         args={},
 538 |     )
 539 | )
 540 | def benchmark(size: int, provider: str):
 541 |     src = torch.randn(size, dtype=DEFAULT_DTYPE, device=DEFAULT_DEVICE)
 542 |     factor = 2.0
 543 | 
 544 |     if provider == "jit":
 545 |         fn = lambda: jit_scale(src, factor)
 546 |     else:
 547 |         fn = lambda: src * factor
 548 | 
 549 |     return run_benchmark(fn)
 550 | 
 551 | 
 552 | if __name__ == "__main__":
 553 |     benchmark.run(print_data=True)
 554 | ```
 555 | 
 556 | Run locally:
 557 | 
 558 | ```bash
 559 | python python/sglang/jit_kernel/benchmark/bench_scale.py
 560 | ```
 561 | 
 562 | Run the benchmark suite the way CI does:
 563 | 
 564 | ```bash
 565 | cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-benchmark-1-gpu-large
 566 | ```
 567 | 
 568 | ---
 569 | 
 570 | ## Troubleshooting
 571 | 
 572 | - **`No CI registry found in ...` from `run_suite.py`**: add a module-level `register_cuda_ci(...)` with literal `est_time` and `suite` (and optional `nightly=True`); starred args and non-literal values break AST collection
 573 | - **JIT compilation fails**: ensure the `.cuh` file is under `python/sglang/jit_kernel/csrc/`; reduce template argument combinations
 574 | - **CUDA crash / illegal memory access**: `CUDA_LAUNCH_BLOCKING=1`; `compute-sanitizer --tool memcheck python ...`
 575 | - **Unstable benchmark results**: `run_benchmark` uses CUDA-graph-based timing by default
 576 | 
 577 | ---
 578 | 
 579 | ## References
 580 | 
 581 | - `docs/developer_guide/development_jit_kernel_guide.md`
 582 | - `test/run_suite.py` — suite names, discovery of `jit_kernel/tests/` and `jit_kernel/benchmark/`, execution entrypoint for CI
 583 | - `python/sglang/test/ci/ci_register.py` — `register_cuda_ci` and AST registration rules
 584 | - `python/sglang/jit_kernel/utils.py` — `cache_once`, `load_jit`, `make_cpp_args`, `should_run_full_tests`, `get_ci_test_range`
 585 | - `python/sglang/jit_kernel/include/sgl_kernel/tensor.h` — `TensorMatcher`, `SymbolicSize/DType/Device`
 586 | - `python/sglang/jit_kernel/include/sgl_kernel/utils.cuh` — type aliases, `LaunchKernel`, `SGL_DEVICE`
 587 | - `python/sglang/jit_kernel/include/sgl_kernel/vec.cuh` — `AlignedVector`
 588 | - `python/sglang/jit_kernel/include/sgl_kernel/tile.cuh` — `tile::Memory`
 589 | - `python/sglang/jit_kernel/include/sgl_kernel/type.cuh` — `dtype_trait`, `packed_t`, `device::cast`
 590 | - `python/sglang/jit_kernel/include/sgl_kernel/math.cuh` — `device::math::`
 591 | - `python/sglang/jit_kernel/include/sgl_kernel/warp.cuh` — `warp::reduce_sum/max`
 592 | - `python/sglang/jit_kernel/include/sgl_kernel/cta.cuh` — `cta::reduce_max`
 593 | - `python/sglang/jit_kernel/include/sgl_kernel/atomic.cuh` — `atomic::max`
 594 | - `python/sglang/jit_kernel/include/sgl_kernel/runtime.cuh` — occupancy / SM count helpers
 595 | - `python/sglang/jit_kernel/csrc/add_constant.cuh` — minimal runnable reference
 596 | - `python/sglang/jit_kernel/csrc/elementwise/rmsnorm.cuh` — real example using `TensorMatcher` + `LaunchKernel` + `tile::Memory`
 597 | - `python/sglang/jit_kernel/csrc/elementwise/qknorm.cuh` — real example using `runtime::get_blocks_per_sm` + persistent kernel pattern
 598 | - `python/sglang/jit_kernel/benchmark/utils.py` — benchmark helpers
 599 | 
 600 | ## Summary of Files Created
 601 | 
 602 | ```
 603 | python/sglang/jit_kernel/csrc/elementwise/scale.cuh   # NEW: CUDA kernel
 604 | python/sglang/jit_kernel/scale.py                     # NEW: Python wrapper
 605 | python/sglang/jit_kernel/tests/test_scale.py          # NEW: Tests
 606 | python/sglang/jit_kernel/benchmark/bench_scale.py     # NEW: Benchmark
 607 | ```
```


---
## .claude/skills/add-sgl-kernel/SKILL.md

```
   1 | ---
   2 | name: add-sgl-kernel
   3 | description: Step-by-step tutorial for adding a heavyweight AOT CUDA/C++ kernel to sgl-kernel (including tests & benchmarks)
   4 | ---
   5 | 
   6 | # Tutorial: Adding a New Kernel to `sgl-kernel` (AOT / Heavyweight)
   7 | 
   8 | This tutorial walks through adding a simple element-wise scale operation as an AOT kernel. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.
   9 | 
  10 | ## Goal
  11 | 
  12 | Add a new operation that scales each element of a tensor by a scalar factor:
  13 | 
  14 | - Input: tensor `x` (CUDA) and scalar `factor` (float)
  15 | - Output: `x * factor` (element-wise, in-place or into pre-allocated `out`)
  16 | - Supported dtypes: **FP16 (`torch.float16`), BF16 (`torch.bfloat16`), FP32 (`torch.float32`)**
  17 |   - Dispatched via `DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16` macro (defined in `sgl-kernel/include/utils.h`)
  18 | 
  19 | ## Two rules of thumb (must follow)
  20 | 
  21 | 1. **Prefer `python/sglang/jit_kernel` first** when the kernel does **not** depend on CUTLASS or another large C++ project. This is the default path for lightweight kernels that benefit from rapid iteration.
  22 | 2. **Prefer `sgl-kernel`** when the kernel **does** depend on CUTLASS or another large C++ project, or when it should be part of the AOT wheel / torch op registration flow.
  23 | 3. **Exception**: if the dependency is `flashinfer`, or CUTLASS that is already provided through `flashinfer`, the kernel can still be implemented as `jit_kernel`.
  24 | 
  25 | In addition, every new kernel must ship with:
  26 | 
  27 | - **Tests** (pytest)
  28 | - **A benchmark script** (triton.testing)
  29 | 
  30 | ---
  31 | 
  32 | ## Repository integration map
  33 | 
  34 | You will typically touch these files/areas:
  35 | 
  36 | - Implementation: `sgl-kernel/csrc/elementwise/scale.cu` (pick the right subdirectory)
  37 | - Public declarations: `sgl-kernel/include/sgl_kernel_ops.h`
  38 | - Torch extension registration: `sgl-kernel/csrc/common_extension.cc`
  39 | - Build: `sgl-kernel/CMakeLists.txt` (`set(SOURCES ...)`)
  40 | - Python API: `sgl-kernel/python/sgl_kernel/` and `sgl-kernel/python/sgl_kernel/__init__.py`
  41 | - Tests: `sgl-kernel/tests/test_scale.py`
  42 | - Benchmarks: `sgl-kernel/benchmark/bench_scale.py`
  43 | 
  44 | ---
  45 | 
  46 | ## Step 1: Implement the kernel in `csrc/`
  47 | 
  48 | Pick the right subdirectory:
  49 | 
  50 | - `csrc/elementwise/` — for element-wise ops (our example)
  51 | - `csrc/gemm/`, `csrc/attention/`, `csrc/moe/` — for other categories
  52 | 
  53 | Create `sgl-kernel/csrc/elementwise/scale.cu`:
  54 | 
  55 | ```cpp
  56 | #include <ATen/cuda/CUDAContext.h>
  57 | #include <c10/cuda/CUDAGuard.h>
  58 | #include <torch/all.h>
  59 | 
  60 | #include "utils.h"  // DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16
  61 | 
  62 | // scale_kernel: out[i] = input[i] * factor
  63 | // Supports float, half (__half), __nv_bfloat16 via template T
  64 | template <typename T>
  65 | __global__ void scale_kernel(T* __restrict__ out,
  66 |                               const T* __restrict__ input,
  67 |                               float factor,
  68 |                               int64_t n) {
  69 |   int64_t idx = static_cast<int64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  70 |   if (idx < n) {
  71 |     out[idx] = static_cast<T>(static_cast<float>(input[idx]) * factor);
  72 |   }
  73 | }
  74 | 
  75 | void scale(at::Tensor& out, const at::Tensor& input, double factor) {
  76 |   TORCH_CHECK(input.is_cuda(),       "input must be a CUDA tensor");
  77 |   TORCH_CHECK(input.is_contiguous(), "input must be contiguous");
  78 |   TORCH_CHECK(out.is_cuda(),         "out must be a CUDA tensor");
  79 |   TORCH_CHECK(out.is_contiguous(),   "out must be contiguous");
  80 |   TORCH_CHECK(out.sizes() == input.sizes(),  "out and input must have the same shape");
  81 |   TORCH_CHECK(out.scalar_type() == input.scalar_type(),
  82 |               "out and input must have the same dtype");
  83 | 
  84 |   const int64_t n = input.numel();
  85 |   const int threads = 256;
  86 |   const int blocks  = (n + threads - 1) / threads;
  87 | 
  88 |   const cudaStream_t stream = at::cuda::getCurrentCUDAStream();
  89 |   const at::cuda::OptionalCUDAGuard device_guard(device_of(input));
  90 | 
  91 |   // Dispatches over float, float16, bfloat16
  92 |   DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16(input.scalar_type(), c_type, [&] {
  93 |     scale_kernel<c_type><<<blocks, threads, 0, stream>>>(
  94 |         static_cast<c_type*>(out.data_ptr()),
  95 |         static_cast<const c_type*>(input.data_ptr()),
  96 |         static_cast<float>(factor),
  97 |         n);
  98 |     cudaError_t status = cudaGetLastError();
  99 |     TORCH_CHECK(status == cudaSuccess,
 100 |                 "scale_kernel launch failed: ", cudaGetErrorString(status));
 101 |     return true;
 102 |   });
 103 | }
 104 | ```
 105 | 
 106 | **Key points:**
 107 | 
 108 | - Use `at::Tensor` (PyTorch tensors), `TORCH_CHECK` for validation, `at::cuda::getCurrentCUDAStream()` for stream
 109 | - Keep Python wrappers thin; do shape/dtype/device validation in C++ right around the launch path
 110 | - `DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16` covers `float`, `half` (FP16), `__nv_bfloat16` (BF16)
 111 | - Add device error checking after every kernel launch
 112 | - If a kernel only works on certain architectures, enforce that with `TORCH_CHECK` and skip logic in tests
 113 | 
 114 | ---
 115 | 
 116 | ## Step 2: Add a C++ declaration in `include/sgl_kernel_ops.h`
 117 | 
 118 | Edit `sgl-kernel/include/sgl_kernel_ops.h`, add to the elementwise section:
 119 | 
 120 | ```cpp
 121 | void scale(at::Tensor& out, const at::Tensor& input, double factor);
 122 | ```
 123 | 
 124 | ---
 125 | 
 126 | ## Step 3: Register the op in `csrc/common_extension.cc`
 127 | 
 128 | Edit `sgl-kernel/csrc/common_extension.cc`, inside `TORCH_LIBRARY_FRAGMENT(sgl_kernel, m)`:
 129 | 
 130 | ```cpp
 131 | // From csrc/elementwise
 132 | m.def("scale(Tensor! out, Tensor input, float factor) -> ()");
 133 | m.impl("scale", torch::kCUDA, &scale);
 134 | ```
 135 | 
 136 | **Key points:**
 137 | 
 138 | - `Tensor!` means in-place / mutable output argument
 139 | - The schema is important for `torch.compile` and for consistent call signatures
 140 | - Keep the torch schema in PyTorch scalar types (`float` here), but note that the C++ launcher signature still needs `double` for scalar arguments accepted by `torch::Library`
 141 | 
 142 | ---
 143 | 
 144 | ## Step 4: Add the new source file to `CMakeLists.txt`
 145 | 
 146 | Edit `sgl-kernel/CMakeLists.txt`, add to `set(SOURCES ...)`:
 147 | 
 148 | ```cmake
 149 | csrc/elementwise/scale.cu
 150 | ```
 151 | 
 152 | **Key points:**
 153 | 
 154 | - Keep the list **alphabetically sorted** (the file explicitly requires this)
 155 | - If the kernel has arch constraints, reflect that in tests/benchmarks via skip logic
 156 | 
 157 | ---
 158 | 
 159 | ## Step 5: Expose a Python API under `sgl-kernel/python/sgl_kernel/`
 160 | 
 161 | Prefer following the existing module organization first. For elementwise kernels, the usual pattern is:
 162 | 
 163 | - implement the Python wrapper in `sgl-kernel/python/sgl_kernel/elementwise.py`
 164 | - then re-export it from `sgl-kernel/python/sgl_kernel/__init__.py`
 165 | 
 166 | For example, in `sgl-kernel/python/sgl_kernel/elementwise.py`, add:
 167 | 
 168 | ```python
 169 | import torch
 170 | 
 171 | def scale(
 172 |     input: torch.Tensor,
 173 |     factor: float,
 174 |     out: torch.Tensor | None = None,
 175 | ) -> torch.Tensor:
 176 |     """
 177 |     Element-wise scale: out = input * factor.
 178 | 
 179 |     Supported dtypes: torch.float16, torch.bfloat16, torch.float32.
 180 | 
 181 |     Parameters
 182 |     ----------
 183 |     input  : CUDA input tensor
 184 |     factor : scale factor (float)
 185 |     out    : optional pre-allocated CUDA output tensor (same shape/dtype as input)
 186 |     """
 187 |     if out is None:
 188 |         out = torch.empty_like(input)
 189 |     torch.ops.sgl_kernel.scale.default(out, input, factor)
 190 |     return out
 191 | ```
 192 | 
 193 | Then re-export it from `sgl-kernel/python/sgl_kernel/__init__.py` following the existing import style used by other kernels.
 194 | 
 195 | ---
 196 | 
 197 | ## Step 6: Write tests (required)
 198 | 
 199 | Create `sgl-kernel/tests/test_scale.py`:
 200 | ```python
 201 | import pytest
 202 | 
 203 | import torch
 204 | import sgl_kernel
 205 | 
 206 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 207 | @pytest.mark.parametrize("size", [128, 1024, 4096, 65536])
 208 | @pytest.mark.parametrize("factor", [0.5, 1.0, 2.0])
 209 | def test_scale_correctness(dtype, size, factor):
 210 |     input = torch.randn(size, dtype=dtype, device="cuda")
 211 |     out   = torch.empty_like(input)
 212 | 
 213 |     result = sgl_kernel.scale(input, factor, out=out)
 214 |     assert result is out
 215 | 
 216 |     expected = input * factor
 217 |     rtol, atol = (1e-5, 1e-6) if dtype == torch.float32 else (1e-2, 1e-2)
 218 |     torch.testing.assert_close(out, expected, rtol=rtol, atol=atol)
 219 | 
 220 | 
 221 | def test_scale_shape_mismatch():
 222 |     input = torch.randn(128, dtype=torch.float16, device="cuda")
 223 |     out   = torch.empty(256, dtype=torch.float16, device="cuda")
 224 |     with pytest.raises(RuntimeError, match="same shape"):
 225 |         sgl_kernel.scale(input, 2.0, out=out)
 226 | 
 227 | 
 228 | def test_scale_cpu_input():
 229 |     input = torch.randn(128, dtype=torch.float16)  # CPU
 230 |     out   = torch.empty_like(input)
 231 |     with pytest.raises(RuntimeError, match="CUDA"):
 232 |         sgl_kernel.scale(input, 2.0, out=out)
 233 | 
 234 | 
 235 | if __name__ == "__main__":
 236 |     import sys
 237 |     sys.exit(pytest.main([__file__, "-q"]))
 238 | ```
 239 | 
 240 | ---
 241 | 
 242 | ## Step 7: Add a benchmark (required)
 243 | 
 244 | Create `sgl-kernel/benchmark/bench_scale.py`:
 245 | 
 246 | ```python
 247 | import itertools
 248 | 
 249 | import torch
 250 | import triton
 251 | import triton.testing
 252 | 
 253 | import sgl_kernel
 254 | from sglang.utils import is_in_ci
 255 | 
 256 | IS_CI = is_in_ci()
 257 | 
 258 | dtypes  = [torch.float16] if IS_CI else [torch.float16, torch.bfloat16, torch.float32]
 259 | sizes   = [4096] if IS_CI else [2**n for n in range(10, 20)]  # 1K … 512K
 260 | factors = [2.0]
 261 | 
 262 | configs = list(itertools.product(dtypes, sizes))
 263 | 
 264 | 
 265 | def torch_scale(input: torch.Tensor, factor: float) -> torch.Tensor:
 266 |     return input * factor
 267 | 
 268 | 
 269 | @triton.testing.perf_report(
 270 |     triton.testing.Benchmark(
 271 |         x_names=["dtype", "size"],
 272 |         x_vals=configs,
 273 |         line_arg="provider",
 274 |         line_vals=["sglang", "torch"],
 275 |         line_names=["SGL Kernel", "PyTorch"],
 276 |         styles=[("green", "-"), ("red", "--")],
 277 |         ylabel="µs (median)",
 278 |         plot_name="scale-performance",
 279 |         args={},
 280 |     )
 281 | )
 282 | def benchmark(dtype, size, provider):
 283 |     input  = torch.randn(size, dtype=dtype, device="cuda")
 284 |     out    = torch.empty_like(input)
 285 |     factor = 2.0
 286 | 
 287 |     if provider == "sglang":
 288 |         fn = lambda: sgl_kernel.scale(input, factor, out=out)
 289 |     else:
 290 |         fn = lambda: torch_scale(input, factor)
 291 | 
 292 |     ms, min_ms, max_ms = triton.testing.do_bench_cudagraph(
 293 |         fn, quantiles=[0.5, 0.2, 0.8]
 294 |     )
 295 |     return 1000 * ms, 1000 * max_ms, 1000 * min_ms
 296 | 
 297 | 
 298 | if __name__ == "__main__":
 299 |     benchmark.run(print_data=True)
 300 | ```
 301 | 
 302 | ---
 303 | 
 304 | ## Step 8: Build
 305 | 
 306 | Build:
 307 | 
 308 | ```bash
 309 | cd sgl-kernel
 310 | make build -j16
 311 | ```
 312 | 
 313 | If you need to limit host resource usage:
 314 | 
 315 | ```bash
 316 | cd sgl-kernel
 317 | make build -j1 MAX_JOBS=2 CMAKE_ARGS="-DSGL_KERNEL_COMPILE_THREADS=1"
 318 | ```
 319 | 
 320 | ---
 321 | 
 322 | ## Step 9: Validate
 323 | 
 324 | After building successfully, run the test and benchmark:
 325 | 
 326 | ```bash
 327 | pytest sgl-kernel/tests/test_scale.py -q
 328 | python sgl-kernel/benchmark/bench_scale.py
 329 | ```
 330 | 
 331 | ---
 332 | 
 333 | ## Troubleshooting
 334 | 
 335 | - **Async CUDA errors**: `CUDA_LAUNCH_BLOCKING=1`
 336 | - **Memory errors**: `compute-sanitizer --tool memcheck python ...`
 337 | - **Build is too slow / OOM**: reduce `MAX_JOBS` and `SGL_KERNEL_COMPILE_THREADS`
 338 | - **Binary bloat**: use `sgl-kernel/analyze_whl_kernel_sizes.py`
 339 | - **CMake sources list**: if your `.cu` file is missing from `SOURCES`, the symbol will be undefined at link time
 340 | 
 341 | ---
 342 | 
 343 | ## References
 344 | 
 345 | - `sgl-kernel/README.md`
 346 | - `sgl-kernel/include/sgl_kernel_ops.h`
 347 | - `sgl-kernel/csrc/common_extension.cc`
 348 | - `sgl-kernel/CMakeLists.txt`
 349 | - `sgl-kernel/include/utils.h` — `DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16` macro and friends
 350 | - `sgl-kernel/csrc/elementwise/activation.cu` — reference for the FP16/BF16/FP32 dispatch pattern
 351 | 
 352 | ## Summary of Files Created/Modified
 353 | 
 354 | ```
 355 | sgl-kernel/csrc/elementwise/scale.cu          # NEW: CUDA kernel + launcher
 356 | sgl-kernel/include/sgl_kernel_ops.h           # MODIFIED: C++ declaration
 357 | sgl-kernel/csrc/common_extension.cc           # MODIFIED: schema + dispatch registration
 358 | sgl-kernel/CMakeLists.txt                     # MODIFIED: add source file (alphabetical)
 359 | sgl-kernel/python/sgl_kernel/elementwise.py   # MODIFIED: Python wrapper
 360 | sgl-kernel/python/sgl_kernel/__init__.py      # MODIFIED: re-export Python API
 361 | sgl-kernel/tests/test_scale.py                # NEW: tests
 362 | sgl-kernel/benchmark/bench_scale.py           # NEW: benchmark
 363 | ```
```


---
## .claude/skills/ci-workflow-guide/SKILL.md

```
   1 | ---
   2 | name: ci-workflow-guide
   3 | description: Guide to SGLang CI workflow orchestration — stage ordering, fast-fail, gating, partitioning, execution modes, and debugging CI failures. Use when modifying CI workflows, adding stages, debugging CI pipeline issues, or understanding how tests are dispatched and gated across stages.
   4 | ---
   5 | 
   6 | # SGLang CI Workflow Orchestration Guide
   7 | 
   8 | This skill covers the CI **infrastructure** layer — how tests are dispatched, gated, and fast-failed across stages. For test authoring (templates, fixtures, registration, model selection), see the [write-sglang-test skill](../write-sglang-test/SKILL.md).
   9 | 
  10 | ---
  11 | 
  12 | ## Naming Conventions
  13 | 
  14 | - **Suite**: `stage-{a,b,c}-test-{gpu_count}-gpu-{hardware}` (e.g., `stage-b-test-1-gpu-small`)
  15 | - **CI runner**: `{gpu_count}-gpu-{hardware}` (e.g., `1-gpu-5090`, `4-gpu-h100`, `8-gpu-h200`)
  16 | 
  17 | ---
  18 | 
  19 | ## Key Files
  20 | 
  21 | | File | Role |
  22 | |------|------|
  23 | | `.github/workflows/pr-test.yml` | Main workflow — all stages, jobs, conditions, matrix definitions |
  24 | | `.github/workflows/pr-gate.yml` | PR gating: draft check, `run-ci` label, per-user rate limiting |
  25 | | `.github/actions/check-stage-health/action.yml` | Cross-job fast-fail: queries API for any failed job |
  26 | | `.github/actions/wait-for-jobs/action.yml` | Stage gating: polls API until stage jobs complete |
  27 | | `.github/actions/check-maintenance/action.yml` | Maintenance mode check |
  28 | | `test/run_suite.py` | Suite runner: collects, filters, partitions, executes tests |
  29 | | `python/sglang/test/ci/ci_register.py` | Test registration (AST-parsed markers), LPT auto-partition |
  30 | | `python/sglang/test/ci/ci_utils.py` | `run_unittest_files()`: execution, retry, continue-on-error |
  31 | | `scripts/ci/utils/slash_command_handler.py` | Handles slash commands from PR comments |
  32 | 
  33 | ---
  34 | 
  35 | ## Architecture Overview
  36 | 
  37 | ```
  38 |  ┌──────────────┐
  39 |  │ build kernel │
  40 |  └──────┬───────┘
  41 |         │
  42 |         ├─ check-changes ──── detects which packages changed
  43 |         │                      (main_package, sgl_kernel, jit_kernel, multimodal_gen)
  44 |         │
  45 |         ├─ call-gate ──────── pr-gate.yml (draft? label? rate limit?)
  46 |         │
  47 |         ├─────────────────────────────────────────────────────┐
  48 |         │                                                     │
  49 |         ▼                                                     │
  50 |  ┌─────────────────────────────────────┐                      │
  51 |  │          Stage A (~3 min)           │                      │
  52 |  │         pre-flight check            │                      │
  53 |  │                                     │                      │
  54 |  │  ┌─────────────────────────────┐    │                      │
  55 |  │  │ stage-a-test-1-gpu-small    │    │                      │
  56 |  │  │ (small GPUs)                │    │                      │
  57 |  │  └─────────────────────────────┘    │                      │
  58 |  │  ┌─────────────────────────────┐    │                      │
  59 |  │  │ stage-a-test-cpu            │    │                      │
  60 |  │  │ (CPU)                       │    │                      │
  61 |  │  └─────────────────────────────┘    │                      │
  62 |  └──────┬──────────────────────────────┘                      │
  63 |         │                                                     │
  64 |         ▼                                                     ▼
  65 |  ┌─────────────────────────────────────┐          ┌──────────────────────────┐
  66 |  │          Stage B (~30 min)          │          │      kernel test         │
  67 |  │           basic tests               │          └──────────────────────────┘
  68 |  │                                     │          ┌──────────────────────────┐
  69 |  │  ┌─────────────────────────────┐    │          │   multimodal gen test    │
  70 |  │  │ stage-b-test-1-gpu-small    │    │          └──────────────────────────┘
  71 |  │  │ (small GPUs, e.g. 5090)     │    │
  72 |  │  └─────────────────────────────┘    │
  73 |  │  ┌─────────────────────────────┐    │
  74 |  │  │ stage-b-test-1-gpu-large    │    │
  75 |  │  │ (large GPUs, e.g. H100)     │    │
  76 |  │  └─────────────────────────────┘    │
  77 |  │  ┌─────────────────────────────┐    │
  78 |  │  │ stage-b-test-2-gpu-large    │    │
  79 |  │  │ (large GPUs, e.g. H100)     │    │
  80 |  │  └─────────────────────────────┘    │
  81 |  └──────┬──────────────────────────────┘
  82 |         │
  83 |         ▼
  84 |  ┌─────────────────────────────────────┐
  85 |  │          Stage C (~30 min)          │
  86 |  │          advanced tests             │
  87 |  │                                     │
  88 |  │  ┌─────────────────────────────┐    │
  89 |  │  │ stage-c-test-4-gpu-h100     │    │
  90 |  │  │ (H100 GPUs)                 │    │
  91 |  │  └─────────────────────────────┘    │
  92 |  │  ┌─────────────────────────────┐    │
  93 |  │  │ stage-c-test-8-gpu-h200     │    │
  94 |  │  │ (8 x H200 GPUs)             │    │
  95 |  │  └─────────────────────────────┘    │
  96 |  │  ┌─────────────────────────────┐    │
  97 |  │  │ stage-c-test-4-gpu-b200     │    │
  98 |  │  │ (4 x B200 GPUs)             │    │
  99 |  │  └─────────────────────────────┘    │
 100 |  │  ┌─────────────────────────────┐    │
 101 |  │  │ Other advanced tests        │    │
 102 |  │  │ (DeepEP, PD Disagg, GB300)  │    │
 103 |  │  └─────────────────────────────┘    │
 104 |  └──────┬──────────────────────────────┘
 105 |         │
 106 |         ▼
 107 |  ┌─────────────────────────────────────┐
 108 |  │         pr-test-finish              │
 109 |  │  aggregates all results, fails if   │
 110 |  │  any job failed/cancelled           │
 111 |  └─────────────────────────────────────┘
 112 | ```
 113 | 
 114 | **Every stage test job** includes a `check-stage-health` step after checkout — if any job in the run has already failed, the job fast-fails (red X) with a root cause annotation.
 115 | 
 116 | **Scheduled runs** skip `wait-for-stage-*` jobs, running all stages in parallel. Fast-fail is also disabled.
 117 | 
 118 | ---
 119 | 
 120 | ## Fast-Fail Layers
 121 | 
 122 | 4 layers of fast-fail, from fine to coarse:
 123 | 
 124 | | Layer | Mechanism | Granularity | Disabled on schedule? |
 125 | |-------|-----------|-------------|----------------------|
 126 | | **1. Test method → file** | `unittest -f` (failfast) | One test method fails → entire test file stops immediately | Yes |
 127 | | **2. File → suite** | `run_unittest_files()` default | One test file fails → entire suite stops (`--continue-on-error` off) | Yes |
 128 | | **3. Job → job (same stage)** | `check-stage-health` action | One job fails → other waiting jobs in same stage fast-fail (red X) | Yes |
 129 | | **4. Stage → stage (cross-stage)** | `wait-for-stage` + `needs` | Stage A fails → stage B/C jobs skip entirely (never get a runner) | Yes (wait jobs skipped) |
 130 | 
 131 | - **Layer 1**: `-f` flag appended to all `python3 -m pytest` / `unittest` invocations in `ci_utils.py`
 132 | - **Layer 2**: `--continue-on-error` flag in `run_suite.py` — off for PRs, on for scheduled runs
 133 | - **Layer 3**: `check-stage-health` auto-detects `schedule` event and skips; filters out cascade failures to show only root cause jobs
 134 | - **Layer 4**: `wait-for-stage-*` jobs are conditioned on `github.event_name == 'pull_request'` — skipped for scheduled runs
 135 | 
 136 | ---
 137 | 
 138 | ## Execution Modes
 139 | 
 140 | | Aspect | PR (`pull_request`) | Scheduled (`cron`, every 6h) | `/rerun-stage` (`workflow_dispatch`) |
 141 | |--------|---------------------|------------------------------|--------------------------------------|
 142 | | **Stage ordering** | Sequential: A → B → C via `wait-for-stage-*` | Parallel (all at once) | Single target stage only |
 143 | | **Cross-job fast-fail** | Yes (`check-stage-health`) | Yes | Yes |
 144 | | **continue-on-error** | No (stop at first failure within suite) | Yes (run all tests) | No |
 145 | | **Retry** | Enabled | Enabled | Enabled |
 146 | | **max_parallel** | 3 (default), 14 if `high priority` label | 14 | 3 (default), 14 if `high priority` |
 147 | | **PR gate** | Yes (draft, label, rate limit) | Skipped | Skipped |
 148 | | **Concurrency** | `cancel-in-progress: true` per branch | Queue (no cancel) | Isolated per stage+SHA |
 149 | 
 150 | ---
 151 | 
 152 | ## Stage Gating (`wait-for-jobs` action)
 153 | 
 154 | `wait-for-stage-a` and `wait-for-stage-b` are lightweight `ubuntu-latest` jobs that poll the GitHub Actions API.
 155 | 
 156 | **How it works:**
 157 | 1. Calls `listJobsForWorkflowRun` to list all jobs in the current run
 158 | 2. Matches jobs by exact name or prefix (for matrix jobs, e.g., `stage-b-test-1-gpu-small (3)`)
 159 | 3. If any matched job has `conclusion === 'failure'` → fail immediately (fast-fail)
 160 | 4. If all matched jobs are completed and count matches `expected_count` → success
 161 | 5. Otherwise → sleep `poll-interval-seconds` (default: 60s) and retry
 162 | 6. Timeout after `max-wait-minutes` (240 min for stage-a, 480 min for stage-b)
 163 | 
 164 | **Job specs example** (stage-b):
 165 | ```json
 166 | [
 167 |   {"prefix": "stage-b-test-1-gpu-small", "expected_count": 8},
 168 |   {"prefix": "stage-b-test-1-gpu-large", "expected_count": 14},
 169 |   {"prefix": "stage-b-test-2-gpu-large", "expected_count": 4},
 170 |   {"prefix": "stage-b-test-4-gpu-b200", "expected_count": 1}
 171 | ]
 172 | ```
 173 | 
 174 | > **Critical**: `expected_count` must match the matrix size. If you add/remove matrix entries, update the wait job's spec accordingly.
 175 | 
 176 | **PR only**: Condition `github.event_name == 'pull_request' && !inputs.target_stage` — scheduled runs and `/rerun-stage` skip these entirely, allowing parallel execution.
 177 | 
 178 | ---
 179 | 
 180 | ## Cross-Job Fast-Fail (`check-stage-health` action)
 181 | 
 182 | Composite action called after checkout in every stage test job (21 jobs total across `pr-test.yml`, `pr-test-multimodal-gen.yml`, `pr-test-sgl-kernel.yml`, `pr-test-jit-kernel.yml`).
 183 | 
 184 | **How it works:**
 185 | 1. Queries `listJobsForWorkflowRun` for the current workflow run
 186 | 2. Filters for **root cause failures only** — jobs with `conclusion === 'failure'` whose failing step is NOT `check-stage-health` (excludes cascade failures)
 187 | 3. If root cause failures found → calls `core.setFailed()` with the list of root cause job names
 188 | 4. If none → does nothing (step succeeds)
 189 | 
 190 | **Cascade filtering**: When job A fast-fails due to health check, it also has `conclusion: failure`. Without filtering, job B would list both the original failure AND job A's fast-fail. The filter checks each failed job's `steps` array — if the failing step name contains `check-stage-health` or `Check stage health`, it's excluded from the root cause list.
 191 | 
 192 | **Usage pattern:**
 193 | ```yaml
 194 | steps:
 195 |   - name: Checkout code
 196 |     uses: actions/checkout@v4
 197 |     ...
 198 | 
 199 |   - uses: ./.github/actions/check-stage-health
 200 |     id: stage-health
 201 | 
 202 |   - name: Install dependencies        # skipped automatically if health check failed
 203 |     ...                                # (default if: success() is false)
 204 | 
 205 |   - name: Run test                     # also skipped
 206 |     ...
 207 | ```
 208 | 
 209 | **Visual effect**: Job shows **red X** (failure) with error annotation showing root cause job names. Subsequent steps are naturally skipped (default `if: success()` is false after a failed step). No per-step `if` guards needed.
 210 | 
 211 | **No stage filtering**: Checks ALL jobs in the run, not just the current stage. Any failure anywhere triggers fast-fail.
 212 | 
 213 | **Error message example:**
 214 | ```
 215 | Fast-fail: skipping — root cause job(s): stage-b-test-1-gpu-small (0), stage-b-test-1-gpu-small (1)
 216 | ```
 217 | 
 218 | ---
 219 | 
 220 | ## Within-Suite Failure Handling
 221 | 
 222 | Controlled by `run_unittest_files()` in `python/sglang/test/ci/ci_utils.py`.
 223 | 
 224 | ### Flags
 225 | 
 226 | | Flag | PR default | Scheduled default | Effect |
 227 | |------|------------|-------------------|--------|
 228 | | `--continue-on-error` | Off | On | Off: stop at first failure. On: run all files, report all failures at end |
 229 | | `--enable-retry` | On | On | Retry retriable failures (accuracy/perf assertions) |
 230 | | `--max-attempts` | 2 | 2 | Max attempts per file including initial run |
 231 | 
 232 | ### Retry Classification
 233 | 
 234 | When a test fails and retry is enabled, the output is classified:
 235 | 
 236 | **Non-retriable** (checked first — real code errors):
 237 | `SyntaxError`, `ImportError`, `ModuleNotFoundError`, `NameError`, `TypeError`, `AttributeError`, `RuntimeError`, `CUDA out of memory`, `OOM`, `Segmentation fault`, `core dumped`, `ConnectionRefusedError`, `FileNotFoundError`
 238 | 
 239 | **Retriable** (accuracy/performance):
 240 | `AssertionError` with comparison patterns (`not greater than`, `not less than`, `not equal to`), `accuracy`, `score`, `latency`, `throughput`, `timeout`
 241 | 
 242 | **Default**: Unknown `AssertionError` → retriable. Other unknown failures → not retriable.
 243 | 
 244 | ### How `continue_on_error` is set
 245 | 
 246 | In `pr-test.yml`'s `check-changes` job:
 247 | - `schedule` runs or `run_all_tests` flag → `continue_on_error = 'true'`
 248 | - PR runs → `continue_on_error = 'false'`
 249 | 
 250 | Each test job propagates via:
 251 | ```yaml
 252 | env:
 253 |   CONTINUE_ON_ERROR_FLAG: ${{ needs.check-changes.outputs.continue_on_error == 'true' && '--continue-on-error' || '' }}
 254 | run: |
 255 |   python3 run_suite.py --hw cuda --suite <name> $CONTINUE_ON_ERROR_FLAG
 256 | ```
 257 | 
 258 | ---
 259 | 
 260 | ## Test Partitioning
 261 | 
 262 | Large suites are split across matrix jobs using the **LPT (Longest Processing Time) heuristic** in `ci_register.py:auto_partition()`:
 263 | 
 264 | 1. Sort tests by `est_time` descending, filename as tie-breaker (deterministic)
 265 | 2. Greedily assign each test to the partition with smallest cumulative time
 266 | 3. Result: roughly equal total time per partition
 267 | 
 268 | **Partition table** (CUDA per-commit suites):
 269 | 
 270 | | Suite | Partitions | Runner | max_parallel |
 271 | |-------|-----------|--------|-------------|
 272 | | `stage-a-test-1-gpu-small` | 1 (no matrix) | `1-gpu-5090` | — |
 273 | | `stage-a-test-cpu` | 1 (no matrix) | `ubuntu-latest` | — |
 274 | | `stage-b-test-1-gpu-small` | 8 | `1-gpu-5090` | 8 |
 275 | | `stage-b-test-1-gpu-large` | 14 | `1-gpu-h100` | dynamic (3 or 14) |
 276 | | `stage-b-test-2-gpu-large` | 4 | `2-gpu-h100` | — |
 277 | | `stage-b-test-4-gpu-b200` | 1 (no matrix) | `4-gpu-b200` | — |
 278 | | `stage-b-kernel-unit-1-gpu-large` | 1 (no matrix) | `1-gpu-h100` | — |
 279 | | `stage-b-kernel-unit-8-gpu-h200` | 1 (no matrix) | `8-gpu-h200` | — |
 280 | | `stage-b-kernel-benchmark-1-gpu-large` | 1 (no matrix) | `1-gpu-h100` | — |
 281 | | `stage-c-test-4-gpu-h100` | 3 | `4-gpu-h100` | — |
 282 | | `stage-c-test-8-gpu-h200` | 4 | `8-gpu-h200` | — |
 283 | | `stage-c-test-8-gpu-h20` | 2 | `8-gpu-h20` | — |
 284 | | `stage-c-test-deepep-4-gpu-h100` | 1 (no matrix) | `4-gpu-h100` | — |
 285 | | `stage-c-test-deepep-8-gpu-h200` | 1 (no matrix) | `8-gpu-h200` | — |
 286 | | `stage-c-test-4-gpu-b200` | 4 | `4-gpu-b200` | — |
 287 | | `stage-c-test-4-gpu-gb200` | 1 (no matrix) | `4-gpu-gb200` | — |
 288 | 
 289 | > **Note**: Kernel suites (`stage-b-kernel-*`) run via `pr-test-jit-kernel.yml` and `pr-test-sgl-kernel.yml`, not the main `pr-test.yml`. Multimodal diffusion uses `python/sglang/multimodal_gen/test/run_suite.py`, not `test/run_suite.py`.
 290 | 
 291 | **Workflow usage:**
 292 | ```yaml
 293 | strategy:
 294 |   matrix:
 295 |     partition: [0, 1, 2, 3, 4, 5, 6, 7]
 296 | steps:
 297 |   - run: python3 run_suite.py --hw cuda --suite stage-b-test-1-gpu-small \
 298 |            --auto-partition-id ${{ matrix.partition }} --auto-partition-size 8
 299 | ```
 300 | 
 301 | ---
 302 | 
 303 | ## check-changes Job
 304 | 
 305 | Determines which test suites to run based on file changes.
 306 | 
 307 | ### Detection Methods
 308 | 
 309 | | Trigger | Method | Details |
 310 | |---------|--------|---------|
 311 | | `pull_request` | `dorny/paths-filter` | Detects changes via GitHub diff |
 312 | | `workflow_dispatch` (with `pr_head_sha`) | GitHub API | `repos/{repo}/compare/main...{sha}` |
 313 | | `schedule` / `run_all_tests` | Force all true | Runs everything |
 314 | 
 315 | ### Output Flags
 316 | 
 317 | | Output | Triggers |
 318 | |--------|----------|
 319 | | `main_package` | Stage A/B/C test suites |
 320 | | `sgl_kernel` | Kernel wheel builds + kernel test suites |
 321 | | `jit_kernel` | JIT kernel test workflow |
 322 | | `multimodal_gen` | Multimodal-gen test workflow |
 323 | 
 324 | > **Note**: `sgl_kernel` is forced to `false` when `target_stage` is set, because `sgl-kernel-build-wheels` won't run and wheel artifacts won't be available.
 325 | 
 326 | ---
 327 | 
 328 | ## Concurrency Control
 329 | 
 330 | ```
 331 | group: pr-test-{event_name}-{branch}-{pr_sha}-{stage}
 332 | ```
 333 | 
 334 | | Segment | Source | Purpose |
 335 | |---------|--------|---------|
 336 | | `event_name` | `github.event_name` | Prevents scheduled runs colliding with fork PRs named `main` |
 337 | | `branch` | `github.head_ref \|\| github.ref_name` | Per-branch isolation |
 338 | | `pr_sha` | `inputs.pr_head_sha \|\| 'current'` | Isolates `/rerun-stage` from main runs |
 339 | | `stage` | `inputs.target_stage \|\| 'all'` | Allows parallel stage dispatches |
 340 | 
 341 | `cancel-in-progress: true` for `pull_request` events (new push cancels old run), `false` for `workflow_call`.
 342 | 
 343 | ---
 344 | 
 345 | ## How To: Add a New Stage Job
 346 | 
 347 | 1. Define the job in `pr-test.yml` with `needs: [check-changes, call-gate, wait-for-stage-X, ...]`
 348 | 2. Copy the `if:` condition pattern from an existing same-stage job (handles `target_stage`, `schedule`, `main_package`)
 349 | 3. Add `checkout` step
 350 | 4. Add `check-stage-health` step (after checkout) — if any prior job failed, `core.setFailed()` fires and all subsequent steps auto-skip via default `if: success()`
 351 | 5. Add `check-maintenance` step
 352 | 6. Add `download-artifact` step if `sgl_kernel` changed
 353 | 7. Add `install dependencies` step
 354 | 8. Add `run test` step with `$CONTINUE_ON_ERROR_FLAG`
 355 | 9. Add `upload-cuda-coredumps` step with `if: always()`
 356 | 10. Register the suite name in `PER_COMMIT_SUITES` in `test/run_suite.py`
 357 | 11. If using matrix, add `--auto-partition-id` and `--auto-partition-size` to the run command
 358 | 12. **Update `wait-for-stage-X`** job spec with the new job name and `expected_count` (if matrix)
 359 | 13. **Add the job to `pr-test-finish.needs`** list
 360 | 
 361 | ---
 362 | 
 363 | ## How To: Debug CI Failures
 364 | 
 365 | | Symptom | Likely cause | What to check |
 366 | |---------|-------------|---------------|
 367 | | All stage-B/C jobs green but steps skipped | Earlier job failed, `check-stage-health` triggered | Find the actual failed job (red X) |
 368 | | `wait-for-stage-b` timeout | `expected_count` doesn't match matrix size | Verify job spec counts match `matrix:` array length |
 369 | | `pr-test-finish` fails but all jobs green | A job was `cancelled` (counts as failure in finish) | Check concurrency cancellation |
 370 | | Tests pass locally but fail in CI | Partition assignment, runner GPU type, or `est_time` inaccuracy | Check which partition the test lands in; verify runner label |
 371 | | Flaky test retried and passed | Retriable failure (accuracy/perf) | Check `[CI Retry]` markers in job logs |
 372 | | Flaky test NOT retried | Matched non-retriable pattern | Check if error matches `NON_RETRIABLE_PATTERNS` in `ci_utils.py` |
 373 | 
 374 | ---
 375 | 
 376 | ## Slash Commands
 377 | 
 378 | | Command | Effect |
 379 | |---------|--------|
 380 | | `/tag-run-ci-label` | Adds `run-ci` label to PR |
 381 | | `/rerun-failed-ci` | Reruns failed jobs in the latest workflow run |
 382 | | `/tag-and-rerun-ci` | Adds label + reruns |
 383 | | `/rerun-stage <stage>` | Dispatches `pr-test.yml` with `target_stage=<stage>` |
 384 | | `/rerun-ut <test-file>` | Reruns a specific test file via `rerun-ut.yml` |
 385 | 
 386 | Handled by `scripts/ci/utils/slash_command_handler.py` → `.github/workflows/slash-command-handler.yml`.
```


---
## .claude/skills/debug-cuda-crash/SKILL.md

```
   1 | ---
   2 | name: debug-cuda-crash
   3 | description: Call this skill when you need to debug CUDA crashes in SGLang using kernel API logging
   4 | ---
   5 | 
   6 | # Tutorial: Debugging CUDA Crashes with Kernel API Logging
   7 | 
   8 | This tutorial shows you how to debug CUDA crashes and errors in SGLang using the `@debug_kernel_api` logging decorator.
   9 | 
  10 | ## Goal
  11 | 
  12 | When your code crashes with CUDA errors such as illegal memory access, device-side assert, out-of-bounds, or NaN/Inf, use kernel API logging to:
  13 | - Capture input tensors BEFORE the crash occurs
  14 | - Understand what data caused the problem
  15 | - Track tensor shapes, dtypes, and values through the call boundary that triggered the crash
  16 | - Detect numerical issues such as NaN, Inf, or obviously wrong shapes
  17 | 
  18 | ## Why Use Kernel API Logging?
  19 | 
  20 | **Problem**: CUDA errors often crash the program before normal debugging output is flushed.
  21 | 
  22 | **Solution**: SGLang's `@debug_kernel_api` decorator logs inputs before execution, so you can still see what caused the crash even after the program aborts.
  23 | 
  24 | ## What Is Covered?
  25 | 
  26 | The current logging coverage focuses on the highest-value kernel boundaries in SGLang:
  27 | - Custom ops registered through `register_custom_op(...)`
  28 | - External custom ops registered through `register_custom_op_from_extern(...)`
  29 | - LLM attention, linear, quantization, and multi-platform wrapper entry points
  30 | - Diffusion attention impl, linear, rotary, and custom-op wrapper entry points
  31 | - Selected direct `torch.ops.sglang.*` hotspots and model-specific bypasses
  32 | 
  33 | This means the logging is useful for both LLM and diffusion kernel debugging, but it does not automatically cover every pure PyTorch call in the repository.
  34 | 
  35 | ## Step 1: Enable Kernel API Logging
  36 | 
  37 | ### Basic Logging (Function Names Only)
  38 | 
  39 | ```bash
  40 | export SGLANG_KERNEL_API_LOGLEVEL=1
  41 | export SGLANG_KERNEL_API_LOGDEST=stdout
  42 | 
  43 | python my_script.py
  44 | ```
  45 | 
  46 | Output:
  47 | ```
  48 | ================================================================================
  49 | [2026-03-19 00:47:06] SGLang Kernel API Call: RMSNorm.forward
  50 | ================================================================================
  51 | [2026-03-19 00:47:06] SGLang Kernel API Call: sglang.quant_method.UnquantizedLinearMethod.apply
  52 | ================================================================================
  53 | [2026-03-19 00:47:06] SGLang Kernel API Call: sglang.custom_op.fused_inplace_qknorm
  54 | ```
  55 | 
  56 | This is a real level-1 excerpt captured from `Qwen/Qwen3-0.6B`.
  57 | 
  58 | ### Detailed Logging (Inputs with Metadata)
  59 | 
  60 | ```bash
  61 | export SGLANG_KERNEL_API_LOGLEVEL=3
  62 | export SGLANG_KERNEL_API_LOGDEST=debug.log
  63 | 
  64 | python my_script.py
  65 | ```
  66 | 
  67 | Output in `debug.log`:
  68 | ```
  69 | ================================================================================
  70 | [2026-03-19 00:47:30] SGLang Kernel API Call: sglang.quant_method.UnquantizedLinearMethod.apply
  71 | Positional input arguments:
  72 |   arg[0]=QKVParallelLinear(
  73 |       repr=QKVParallelLinear(in_features=1024, output_features=4096, bias=False, tp_size=1, gather_output=False)
  74 |     )
  75 |   arg[1]=Tensor(
  76 |       shape=(1, 1024)
  77 |       dtype=torch.bfloat16
  78 |       device=cuda:0
  79 |       requires_grad=False
  80 |       is_contiguous=True
  81 |     )
  82 |   arg[2]=None
  83 | Output:
  84 |   return=Tensor(
  85 |       shape=(1, 4096)
  86 |       dtype=torch.bfloat16
  87 |       device=cuda:0
  88 |       requires_grad=False
  89 |       is_contiguous=True
  90 |     )
  91 | ```
  92 | 
  93 | This is a real level-3 excerpt captured from `Qwen/Qwen3-0.6B`.
  94 | 
  95 | ### Full Logging (With Tensor Statistics)
  96 | 
  97 | ```bash
  98 | export SGLANG_KERNEL_API_LOGLEVEL=5
  99 | export SGLANG_KERNEL_API_LOGDEST=debug.log
 100 | 
 101 | python my_script.py
 102 | ```
 103 | 
 104 | Additional output:
 105 | ```
 106 | ================================================================================
 107 | [2026-03-19 01:00:42] SGLang Kernel API Call: diffusion.quant_method.UnquantizedLinearMethod.apply
 108 | Positional input arguments:
 109 |   arg[1]=Tensor(
 110 |       shape=(1, 77, 768)
 111 |       dtype=torch.bfloat16
 112 |       device=cuda:0
 113 |       requires_grad=False
 114 |       is_contiguous=True
 115 |       min=-27.250000
 116 |       max=28.500000
 117 |       mean=0.011723
 118 |       nan_count=0
 119 |       inf_count=0
 120 |     )
 121 | Output:
 122 |   return=Tensor(
 123 |       shape=(1, 77, 2304)
 124 |       dtype=torch.bfloat16
 125 |       device=cuda:0
 126 |       requires_grad=False
 127 |       is_contiguous=True
 128 |       min=-8.937500
 129 |       max=9.375000
 130 |       mean=0.009460
 131 |       nan_count=0
 132 |       inf_count=0
 133 |     )
 134 | ```
 135 | 
 136 | This is a real level-5 excerpt captured from `black-forest-labs/FLUX.1-dev`.
 137 | 
 138 | ### Crash-Safe Dumps (Inputs Saved Before Execution)
 139 | 
 140 | ```bash
 141 | export SGLANG_KERNEL_API_LOGLEVEL=10
 142 | export SGLANG_KERNEL_API_LOGDEST=debug.log
 143 | export SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_kernel_api_dumps
 144 | 
 145 | python my_script.py
 146 | ```
 147 | 
 148 | At level 10, SGLang saves the inputs before execution. If the kernel crashes, the dump directory still contains the inputs and exception metadata.
 149 | 
 150 | If CUDA graph capture is active, tensor dumps are skipped automatically to avoid capture-time CUDA errors. In that case, you still get the kernel API call log, but not `inputs.pt` / `outputs.pt`.
 151 | 
 152 | Level-10 dumps are best understood as crash-safe call snapshots. They always preserve the observed call boundary. They do not guarantee one-click replay for every method, because some methods depend on module state that is not serialized into the dump.
 153 | 
 154 | Real level-10 dump layout from `Qwen/Qwen3-0.6B`:
 155 | 
 156 | ```text
 157 | /tmp/sglang_kernel_api_validation/qwen_qwen3_0_6b_level10_dumps
 158 | /tmp/sglang_kernel_api_validation/qwen_qwen3_0_6b_level10_dumps/20260319_004821_182_pid919286_RotaryEmbedding.forward_call0001
 159 | /tmp/sglang_kernel_api_validation/qwen_qwen3_0_6b_level10_dumps/20260319_004821_182_pid919286_RotaryEmbedding.forward_call0001/inputs.pt
 160 | /tmp/sglang_kernel_api_validation/qwen_qwen3_0_6b_level10_dumps/20260319_004821_182_pid919286_RotaryEmbedding.forward_call0001/metadata.json
 161 | /tmp/sglang_kernel_api_validation/qwen_qwen3_0_6b_level10_dumps/20260319_004821_182_pid919286_RotaryEmbedding.forward_call0001/outputs.pt
 162 | ```
 163 | 
 164 | Real `metadata.json` excerpt:
 165 | 
 166 | ```json
 167 | {
 168 |   "function_name": "RotaryEmbedding.forward",
 169 |   "timestamp": "20260319_004821_182",
 170 |   "process_id": 919286,
 171 |   "execution_status": "completed",
 172 |   "input_tensor_keys": ["arg_0", "arg_1", "arg_2"],
 173 |   "output_tensor_keys": ["result_0", "result_1"]
 174 | }
 175 | ```
 176 | 
 177 | ## Step 2: Reproduce an LLM CUDA Crash
 178 | 
 179 | Create a temporary reproducer:
 180 | 
 181 | ```bash
 182 | python3 - <<'PY'
 183 | from pathlib import Path
 184 | Path("/tmp/sglang_llm_crash.py").write_text(
 185 |     "import torch\\n"
 186 |     "import torch.nn.functional as F\\n"
 187 |     "from sglang.srt.utils.custom_op import register_custom_op\\n\\n"
 188 |     "def _fake_embedding(indices, table):\\n"
 189 |     "    return torch.empty((*indices.shape, table.shape[-1]), device=table.device, dtype=table.dtype)\\n\\n"
 190 |     "@register_custom_op(op_name='mock_llm_cuda_crash', fake_impl=_fake_embedding)\\n"
 191 |     "def mock_llm_cuda_crash(indices, table):\\n"
 192 |     "    out = F.embedding(indices, table)\\n"
 193 |     "    torch.cuda.synchronize()\\n"
 194 |     "    return out\\n\\n"
 195 |     "table = torch.randn(4, 8, device='cuda', dtype=torch.float16)\\n"
 196 |     "indices = torch.tensor([0, 7], device='cuda', dtype=torch.long)\\n"
 197 |     "mock_llm_cuda_crash(indices, table)\\n"
 198 | )
 199 | PY
 200 | 
 201 | SGLANG_KERNEL_API_LOGLEVEL=1 \
 202 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_llm_level1.log \
 203 | python3 /tmp/sglang_llm_crash.py
 204 | ```
 205 | 
 206 | What to expect:
 207 | - The script exits with a CUDA `device-side assert`
 208 | - The log still contains the last API boundary before the crash
 209 | 
 210 | Try the same example at level 3:
 211 | 
 212 | ```bash
 213 | SGLANG_KERNEL_API_LOGLEVEL=3 \
 214 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_llm_level3.log \
 215 | python3 /tmp/sglang_llm_crash.py
 216 | ```
 217 | 
 218 | Now the log shows tensor metadata before the crash.
 219 | 
 220 | Try level 10:
 221 | 
 222 | ```bash
 223 | SGLANG_KERNEL_API_LOGLEVEL=10 \
 224 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_llm_level10.log \
 225 | SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_llm_level10_dumps \
 226 | python3 /tmp/sglang_llm_crash.py
 227 | ```
 228 | 
 229 | Now you should see:
 230 | - A log entry for `sglang.custom_op.mock_llm_cuda_crash`
 231 | - A dump directory with `inputs.pt`
 232 | - `metadata.json` showing `execution_status: "exception"`
 233 | - No `outputs.pt`, because the kernel crashed before producing output
 234 | 
 235 | For real-model success-path level-10 dumps, it is often easier to temporarily disable CUDA graph and piecewise CUDA graph for the debug run.
 236 | 
 237 | ## Step 3: Reproduce a Diffusion CUDA Crash
 238 | 
 239 | Create a temporary diffusion-side reproducer:
 240 | 
 241 | ```bash
 242 | python3 - <<'PY'
 243 | from pathlib import Path
 244 | Path("/tmp/sglang_diffusion_crash.py").write_text(
 245 |     "import torch\\n"
 246 |     "import torch.nn.functional as F\\n"
 247 |     "from sglang.multimodal_gen.runtime.layers.utils import register_custom_op\\n\\n"
 248 |     "def _fake_embedding(positions, cache):\\n"
 249 |     "    return torch.empty((*positions.shape, cache.shape[-1]), device=cache.device, dtype=cache.dtype)\\n\\n"
 250 |     "@register_custom_op(op_name='mock_diffusion_cuda_crash', fake_impl=_fake_embedding)\\n"
 251 |     "def mock_diffusion_cuda_crash(positions, cache):\\n"
 252 |     "    out = F.embedding(positions, cache)\\n"
 253 |     "    torch.cuda.synchronize()\\n"
 254 |     "    return out\\n\\n"
 255 |     "cache = torch.randn(4, 64, device='cuda', dtype=torch.float16)\\n"
 256 |     "positions = torch.tensor([0, 9], device='cuda', dtype=torch.long)\\n"
 257 |     "mock_diffusion_cuda_crash(positions, cache)\\n"
 258 | )
 259 | PY
 260 | 
 261 | SGLANG_KERNEL_API_LOGLEVEL=1 \
 262 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level1.log \
 263 | python3 /tmp/sglang_diffusion_crash.py
 264 | ```
 265 | 
 266 | Try level 3:
 267 | 
 268 | ```bash
 269 | SGLANG_KERNEL_API_LOGLEVEL=3 \
 270 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level3.log \
 271 | python3 /tmp/sglang_diffusion_crash.py
 272 | ```
 273 | 
 274 | Try level 10:
 275 | 
 276 | ```bash
 277 | SGLANG_KERNEL_API_LOGLEVEL=10 \
 278 | SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level10.log \
 279 | SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_diffusion_level10_dumps \
 280 | python3 /tmp/sglang_diffusion_crash.py
 281 | ```
 282 | 
 283 | If your local environment has unrelated FlashInfer import issues, resolve them in the shell before running the example. The example itself does not set any `FLASHINFER_*` environment variable.
 284 | 
 285 | ## Step 4: Multi-Process Debugging
 286 | 
 287 | When running with multiple GPUs or worker processes, use `%i` in the log path:
 288 | 
 289 | ```bash
 290 | export SGLANG_KERNEL_API_LOGLEVEL=3
 291 | export SGLANG_KERNEL_API_LOGDEST=debug_rank_%i.log
 292 | 
 293 | torchrun --nproc_per_node=4 my_script.py
 294 | ```
 295 | 
 296 | This creates separate logs such as:
 297 | - `debug_rank_12345.log`
 298 | - `debug_rank_12346.log`
 299 | - `debug_rank_12347.log`
 300 | - `debug_rank_12348.log`
 301 | 
 302 | Real multi-process example from a 2-GPU `Qwen/Qwen2.5-0.5B-Instruct` run:
 303 | 
 304 | ```text
 305 | /tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950201.log
 306 | /tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950349.log
 307 | /tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950350.log
 308 | /tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950351.log
 309 | ```
 310 | 
 311 | You should usually do the same for level-10 dump directories:
 312 | 
 313 | ```bash
 314 | export SGLANG_KERNEL_API_LOGLEVEL=10
 315 | export SGLANG_KERNEL_API_LOGDEST=debug_rank_%i.log
 316 | export SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_kernel_api_dumps_%i
 317 | ```
 318 | 
 319 | This avoids multiple ranks writing into the same dump directory tree.
 320 | 
 321 | ## Step 5: Filter Level-10 Dumps
 322 | 
 323 | If level 10 is too noisy, restrict dumps to specific APIs:
 324 | 
 325 | ```bash
 326 | export SGLANG_KERNEL_API_LOGLEVEL=10
 327 | export SGLANG_KERNEL_API_LOGDEST=debug.log
 328 | export SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_kernel_api_dumps
 329 | export SGLANG_KERNEL_API_DUMP_INCLUDE='sglang.custom_op.*'
 330 | export SGLANG_KERNEL_API_DUMP_EXCLUDE='*.fake_impl'
 331 | ```
 332 | 
 333 | `SGLANG_KERNEL_API_DUMP_INCLUDE` and `SGLANG_KERNEL_API_DUMP_EXCLUDE` use shell-style wildcard matching.
 334 | 
 335 | ## Step 6: Common CUDA Errors and What to Check
 336 | 
 337 | ### Illegal Memory Access or Device-Side Assert
 338 | 
 339 | **Typical errors**:
 340 | ```
 341 | RuntimeError: CUDA error: an illegal memory access was encountered
 342 | torch.AcceleratorError: CUDA error: device-side assert triggered
 343 | ```
 344 | 
 345 | Use:
 346 | 
 347 | ```bash
 348 | export SGLANG_KERNEL_API_LOGLEVEL=3
 349 | ```
 350 | 
 351 | Check in the logs:
 352 | - ✅ Tensor shapes
 353 | - ✅ Tensor dtypes
 354 | - ✅ CUDA vs CPU device placement
 355 | - ✅ Tensor stride / contiguity
 356 | - ✅ Whether the failing call has inputs logged but no outputs logged
 357 | 
 358 | Typical shape-mismatch pattern:
 359 | 
 360 | ```text
 361 | SGLang Kernel API Call: ...
 362 | arg[0]=Tensor(shape=(..., 128), ...)   # ✅ expected dimension
 363 | arg[1]=Tensor(shape=(..., 64), ...)    # ❌ mismatch
 364 | ```
 365 | 
 366 | This often points to head-dim, hidden-dim, or cache-layout mismatch rather than a random CUDA failure.
 367 | 
 368 | ### NaN or Inf
 369 | 
 370 | Use:
 371 | 
 372 | ```bash
 373 | export SGLANG_KERNEL_API_LOGLEVEL=5
 374 | ```
 375 | 
 376 | Check:
 377 | - `min`
 378 | - `max`
 379 | - `mean`
 380 | - `nan_count`
 381 | - `inf_count`
 382 | 
 383 | Typical bad pattern:
 384 | 
 385 | ```text
 386 | Tensor(
 387 |   ...
 388 |   min=-1234567.000000   # ❌ suspiciously large
 389 |   max=9876543.000000    # ❌ suspiciously large
 390 |   mean=nan              # ❌ bad
 391 |   nan_count=128         # ❌ found NaNs
 392 |   inf_count=0           # ✅ no Infs here
 393 | )
 394 | ```
 395 | 
 396 | This usually means the bad values were already present before the crashing kernel.
 397 | 
 398 | ### Out of Memory
 399 | 
 400 | Use:
 401 | 
 402 | ```bash
 403 | export SGLANG_KERNEL_API_LOGLEVEL=3
 404 | ```
 405 | 
 406 | Check:
 407 | - Unexpectedly large tensor shapes
 408 | - Batch size
 409 | - Sequence length
 410 | - Frame count or image resolution in diffusion workloads
 411 | 
 412 | Also check whether a supposedly per-token or per-frame tensor accidentally became full-sequence or full-image sized.
 413 | 
 414 | Typical bad pattern:
 415 | 
 416 | ```text
 417 | Tensor(
 418 |   shape=(1024, 8192, 128, 128)   # ❌ way too large
 419 |   ...
 420 | )
 421 | ```
 422 | 
 423 | ### Example: Spot a Shape Bug from the Log
 424 | 
 425 | Suppose the failing API log looks like this:
 426 | 
 427 | ```text
 428 | [2026-03-19 00:47:30] SGLang Kernel API Call: RotaryEmbedding.forward
 429 | Positional input arguments:
 430 |   arg[0]=Tensor(shape=(1, 8), dtype=torch.int64, ...)
 431 |   arg[1]=Tensor(shape=(1, 8, 8, 256), dtype=torch.bfloat16, ...)    # ✅ query
 432 |   arg[2]=Tensor(shape=(1, 8, 4, 64), dtype=torch.bfloat16, ...)     # ❌ key head_dim mismatch
 433 | ```
 434 | 
 435 | What this tells you:
 436 | - ✅ positions look reasonable
 437 | - ✅ query looks plausible
 438 | - ❌ key last dimension is inconsistent with the expected rotary/head dimension
 439 | 
 440 | That usually means the bug is in projection layout, head packing, or cache format rather than in the rotary kernel itself.
 441 | 
 442 | ## Step 7: Combine with compute-sanitizer
 443 | 
 444 | For harder bugs, combine kernel API logging with CUDA memory checking:
 445 | 
 446 | ```bash
 447 | export SGLANG_KERNEL_API_LOGLEVEL=3
 448 | export SGLANG_KERNEL_API_LOGDEST=debug.log
 449 | 
 450 | compute-sanitizer --tool memcheck python3 /tmp/sglang_llm_crash.py
 451 | ```
 452 | 
 453 | Use `debug.log` to see the exact inputs that reached the crashing API boundary.
 454 | 
 455 | Typical `compute-sanitizer` output:
 456 | 
 457 | ```text
 458 | ========= COMPUTE-SANITIZER
 459 | ========= Invalid __global__ write of size 4 bytes
 460 | =========     at 0x1234 in SomeKernel
 461 | =========     by thread (256,0,0) in block (10,0,0)
 462 | =========     Address 0x... is out of bounds
 463 | ```
 464 | 
 465 | Use the sanitizer output to identify the failing kernel and use `debug.log` to identify the exact tensors that reached the API boundary right before it.
 466 | 
 467 | If you need more synchronous host-side error reporting, you can try `CUDA_LAUNCH_BLOCKING=1` as a separate follow-up experiment. It is not part of the default workflow because it changes execution timing and can hide concurrency-related behavior.
 468 | 
 469 | ## Step 8: Combine with cuda-gdb
 470 | 
 471 | For crashes that need a stack trace instead of only memory diagnostics:
 472 | 
 473 | ```bash
 474 | export SGLANG_KERNEL_API_LOGLEVEL=3
 475 | export SGLANG_KERNEL_API_LOGDEST=debug.log
 476 | 
 477 | cuda-gdb --args python3 /tmp/sglang_llm_crash.py
 478 | ```
 479 | 
 480 | Inside `cuda-gdb`:
 481 | 
 482 | ```text
 483 | (cuda-gdb) run
 484 | (cuda-gdb) where
 485 | ```
 486 | 
 487 | Then correlate the backtrace with `debug.log`.
 488 | 
 489 | ## Step 9: Kernel-Level Debugging with printf()
 490 | 
 491 | When you own the CUDA kernel, `printf()` is still useful for narrowing down bad indices, bad launch geometry, or broken state propagation.
 492 | 
 493 | Basic pattern:
 494 | 
 495 | ```cpp
 496 | __global__ void MyKernel(const float* input, float* output, int n) {
 497 |   int idx = blockIdx.x * blockDim.x + threadIdx.x;
 498 | 
 499 |   if (threadIdx.x == 0 && blockIdx.x == 0) {
 500 |     printf("n=%d input0=%f\n", n, input[0]);
 501 |   }
 502 | 
 503 |   if (idx < n) {
 504 |     output[idx] = input[idx] * 2.0f;
 505 |   }
 506 | }
 507 | ```
 508 | 
 509 | After launch, force the output to flush:
 510 | 
 511 | ```python
 512 | my_kernel(...)
 513 | torch.cuda.synchronize()
 514 | ```
 515 | 
 516 | For warp-specialized kernels, do not blindly print only on `threadIdx.x == 0`. Pick one representative thread per warp or per specialization group instead.
 517 | 
 518 | ### Warp-Specialized Kernels: Choosing the Right Print Thread
 519 | 
 520 | Problem:
 521 | - `threadIdx.x == 0` only prints from the first warp in the block
 522 | - for warp-specialized kernels, that often misses the warp or group that is actually wrong
 523 | 
 524 | Better pattern:
 525 | 
 526 | ```cpp
 527 | __global__ void WarpSpecializedKernel(...) {
 528 |   // Example: first lane of each warp
 529 |   if ((threadIdx.x % 32) == 0) {
 530 |     printf("warp=%d\n", threadIdx.x / 32);
 531 |   }
 532 | }
 533 | ```
 534 | 
 535 | Or, if the kernel is organized in larger specialization groups, print once per group instead of once per block.
 536 | 
 537 | Common mistake:
 538 | 
 539 | ```cpp
 540 | // Only warp 0 prints
 541 | if (threadIdx.x == 0) {
 542 |   printf("warp=%d\n", threadIdx.x / 32);
 543 | }
 544 | ```
 545 | 
 546 | ### Quick Reference
 547 | 
 548 | | Kernel Type | Print Condition | Notes |
 549 | |----------|----------|-------------|
 550 | | Simple kernel | `threadIdx.x == 0` | One thread per block is usually enough |
 551 | | Warp-specialized kernel | one representative lane per warp | e.g. `threadIdx.x % 32 == 0` |
 552 | | Group-specialized kernel | one representative lane per group | choose based on the kernel's scheduling layout |
 553 | 
 554 | ### Other Kernel Debugging Tools
 555 | 
 556 | ```cpp
 557 | assert(value >= 0.0f && "value must be non-negative");
 558 | static_assert(BLOCK_SIZE % 32 == 0, "BLOCK_SIZE must be warp aligned");
 559 | ```
 560 | 
 561 | ## Environment Variables Reference
 562 | 
 563 | | Variable | Values | Description |
 564 | |----------|--------|-------------|
 565 | | `SGLANG_KERNEL_API_LOGLEVEL` | `0` | No logging (default) |
 566 | |  | `1` | Function names only |
 567 | |  | `3` | Inputs and outputs with metadata |
 568 | |  | `5` | Level 3 plus tensor statistics |
 569 | |  | `10` | Level 5 plus crash-safe tensor dumps |
 570 | | `SGLANG_KERNEL_API_LOGDEST` | `stdout` | Log to stdout |
 571 | |  | `stderr` | Log to stderr |
 572 | |  | `<path>` | Log to file |
 573 | |  | `log_%i.txt` | `%i` expands to process ID |
 574 | | `SGLANG_KERNEL_API_DUMP_DIR` | `<path>` | Directory for level-10 dumps |
 575 | | `SGLANG_KERNEL_API_DUMP_INCLUDE` | wildcard list | Only dump matching API names |
 576 | | `SGLANG_KERNEL_API_DUMP_EXCLUDE` | wildcard list | Skip matching API names |
 577 | 
 578 | ## Best Practices
 579 | 
 580 | ### 1. Start with Level 3
 581 | 
 582 | ```bash
 583 | export SGLANG_KERNEL_API_LOGLEVEL=3
 584 | ```
 585 | 
 586 | Level 3 is usually enough to catch wrong shapes, wrong dtypes, and wrong devices.
 587 | 
 588 | ### 2. Use Level 5 for Numerical Issues
 589 | 
 590 | ```bash
 591 | export SGLANG_KERNEL_API_LOGLEVEL=5
 592 | ```
 593 | 
 594 | Use it when you suspect NaN or Inf values.
 595 | 
 596 | ### 3. Use Level 10 for Crash Reproduction
 597 | 
 598 | ```bash
 599 | export SGLANG_KERNEL_API_LOGLEVEL=10
 600 | ```
 601 | 
 602 | This is the most useful mode when the process crashes before you can inspect live tensors.
 603 | 
 604 | If you need successful input/output dumps from a real model run, temporarily disable CUDA graph for that debug session.
 605 | 
 606 | When level 10 is too noisy, pair it with `SGLANG_KERNEL_API_DUMP_INCLUDE` / `SGLANG_KERNEL_API_DUMP_EXCLUDE` instead of dumping every covered API.
 607 | 
 608 | ### 4. Log to File for Crashes
 609 | 
 610 | ```bash
 611 | export SGLANG_KERNEL_API_LOGDEST=crash.log
 612 | ```
 613 | 
 614 | File logs are safer than stdout when the process aborts.
 615 | 
 616 | ### 5. Disable Logging in Production
 617 | 
 618 | ```bash
 619 | unset SGLANG_KERNEL_API_LOGLEVEL
 620 | ```
 621 | 
 622 | When disabled, the decorator returns the original callable and adds no runtime logging overhead.
 623 | 
 624 | ## Troubleshooting
 625 | 
 626 | ### No Logs Appear
 627 | 
 628 | Check:
 629 | 1. `echo $SGLANG_KERNEL_API_LOGLEVEL`
 630 | 2. `echo $SGLANG_KERNEL_API_LOGDEST`
 631 | 3. Whether the failing path goes through a covered API boundary
 632 | 
 633 | ### Too Much Output
 634 | 
 635 | Reduce the level:
 636 | 
 637 | ```bash
 638 | export SGLANG_KERNEL_API_LOGLEVEL=3
 639 | ```
 640 | 
 641 | ### Statistics Are Skipped During CUDA Graph Capture
 642 | 
 643 | If you see:
 644 | ```text
 645 | statistics=[skipped: CUDA graph capture in progress]
 646 | ```
 647 | 
 648 | That is expected. Level-5 statistics are intentionally skipped during CUDA graph capture to avoid synchronization side effects.
 649 | 
 650 | ### Tensor Dumps Are Skipped During CUDA Graph Capture
 651 | 
 652 | If you see:
 653 | ```text
 654 | Tensor dump skipped: CUDA graph capture in progress
 655 | ```
 656 | 
 657 | That is also expected. Level-10 dumps require copying tensors to CPU, which is not allowed during CUDA graph capture.
```


---
## .claude/skills/generate-profile/SKILL.md

```
   1 | ---
   2 | name: generate-profile
   3 | description: Generate an e2e profiling trace of an SGLang server run. Launches a server, validates accuracy, captures a Chrome-compatible trace, and returns the profile path.
   4 | ---
   5 | 
   6 | # Generate an E2E Profile of an SGLang Server Run
   7 | 
   8 | This skill launches an SGLang server, validates it with a quick accuracy test, generates a profiling trace, and returns the profile file path.
   9 | 
  10 | ## Prerequisites
  11 | 
  12 | - A working SGLang installation (`pip install -e .` or equivalent)
  13 | - At least one available CUDA GPU
  14 | 
  15 | ## Step-by-step Workflow
  16 | 
  17 | ### Step 1: Launch the server
  18 | 
  19 | ```bash
  20 | CUDA_VISIBLE_DEVICES=<gpu_id> sglang serve --model-path <model> --port <port> &
  21 | ```
  22 | 
  23 | - Default model: `Qwen/Qwen3-8B` (good balance of speed and quality)
  24 | - Default port: `30000`
  25 | - The server runs in the background. Save the PID for cleanup.
  26 | - Use the GPU specified by the user's preferences (check memory files for GPU preferences).
  27 | 
  28 | ### Step 2: Wait for server readiness
  29 | 
  30 | Poll the health endpoint until the server is ready:
  31 | 
  32 | ```bash
  33 | for i in $(seq 1 120); do
  34 |   if curl -s http://127.0.0.1:<port>/health 2>/dev/null | grep -q "ok\|healthy"; then
  35 |     echo "Server ready"
  36 |     break
  37 |   fi
  38 |   sleep 5
  39 | done
  40 | ```
  41 | 
  42 | The server prints **"The server is fired up and ready to roll!"** to stdout when ready. The health endpoint returns 200 once the server can accept requests.
  43 | 
  44 | Typical startup time: 30-90 seconds depending on model size and whether CUDA graphs are being compiled.
  45 | 
  46 | ### Step 3: Validate accuracy (sanity check)
  47 | 
  48 | ```bash
  49 | python3 -m sglang.test.few_shot_gsm8k --num-q 20
  50 | ```
  51 | 
  52 | - Expected accuracy: **> 0.8** for capable models (Qwen3-8B, Llama-3.1-8B-Instruct, etc.)
  53 | - This is a quick sanity check, not a rigorous benchmark.
  54 | - If accuracy is unexpectedly low, something is wrong — do not proceed to profiling.
  55 | 
  56 | ### Step 4: Generate the profile
  57 | 
  58 | ```bash
  59 | python3 -m sglang.test.send_one --profile
  60 | ```
  61 | 
  62 | This command:
  63 | 1. Sends a request to the server
  64 | 2. Triggers the profiler for 5 steps (default)
  65 | 3. Generates a trace file under `/tmp/<timestamp>/`
  66 | 4. The trace directory contains:
  67 |    - `<timestamp>-TP-0.trace.json.gz` — Chrome trace format (open in `chrome://tracing` or Perfetto)
  68 |    - `server_args.json` — the server configuration used
  69 | 
  70 | **Output format:**
  71 | ```
  72 | Dump profiling traces to /tmp/<timestamp>
  73 | ```
  74 | 
  75 | The profile path is printed to stdout. Parse it from the output.
  76 | 
  77 | **Optional flags:**
  78 | - `--profile-steps N` — number of profiling steps (default: 5)
  79 | - `--profile-by-stage` — profile by stage (prefill/decode separately)
  80 | - `--profile-prefix <path>` — custom output prefix
  81 | 
  82 | ### Step 5: Kill the server
  83 | 
  84 | ```bash
  85 | pkill -9 -f "sglang.launch_server\|sglang serve\|sglang.srt"
  86 | ```
  87 | 
  88 | Wait a moment and verify no sglang processes remain:
  89 | ```bash
  90 | sleep 2 && pgrep -af "sglang serve" || echo "Server killed"
  91 | ```
  92 | 
  93 | ### Step 6: Report the profile path
  94 | 
  95 | Return the profile directory path (e.g., `/tmp/1773999986.4769795`) and list its contents so the user knows what files were generated.
  96 | 
  97 | ## Example Full Run
  98 | 
  99 | ```bash
 100 | # 1. Launch server
 101 | source cleanup/bin/activate
 102 | CUDA_VISIBLE_DEVICES=1 sglang serve --model-path Qwen/Qwen3-8B --port 30000 &
 103 | 
 104 | # 2. Wait for ready
 105 | for i in $(seq 1 120); do
 106 |   curl -s http://127.0.0.1:30000/health | grep -q "ok" && break
 107 |   sleep 5
 108 | done
 109 | 
 110 | # 3. Accuracy check
 111 | python3 -m sglang.test.few_shot_gsm8k --num-q 20
 112 | # Expected: Accuracy > 0.8
 113 | 
 114 | # 4. Profile
 115 | python3 -m sglang.test.send_one --profile
 116 | # Output: "Dump profiling traces to /tmp/1773999986.4769795"
 117 | 
 118 | # 5. Cleanup
 119 | pkill -9 -f "sglang.launch_server\|sglang serve\|sglang.srt"
 120 | sleep 2
 121 | 
 122 | # 6. Check output
 123 | ls -la /tmp/1773999986.4769795/
 124 | # 1773999986.4851577-TP-0.trace.json.gz  (Chrome trace)
 125 | # server_args.json                        (server config)
 126 | ```
 127 | 
 128 | ## Customization
 129 | 
 130 | - **Different port**: Pass `--port <port>` and use `--host 127.0.0.1 --port <port>` for test commands
 131 | - **Multi-GPU**: Use `--tp <N>` for tensor parallelism; trace files will be generated per TP rank
 132 | - **Longer profile**: Use `--profile-steps 10` for more steps in the trace
 133 | - **Stage profiling**: Use `--profile-by-stage` to separate prefill and decode phases
 134 | 
 135 | ## Viewing the Profile
 136 | 
 137 | Open the `.trace.json.gz` file in:
 138 | - **Perfetto UI**: https://ui.perfetto.dev/ (drag and drop the file)
 139 | - **Chrome tracing**: `chrome://tracing` (load the file)
 140 | 
 141 | Both support the gzipped Chrome trace format natively.
```


---
## .claude/skills/sglang-bisect-ci-regression/SKILL.md

```
   1 | # SGLang Bisect CI Regression
   2 | 
   3 | Investigate a consistently failing CI test to find the root cause - whether it's a code regression from a specific PR, a hardware/runner-specific issue, or an environment change. Optionally reproduce the failure on a remote GPU server.
   4 | 
   5 | ## Slash Command
   6 | 
   7 | `/sglang-bisect-ci-regression <test_name_or_ci_url> [ssh_target] [docker_container]`
   8 | 
   9 | ## When to Use This Skill
  10 | 
  11 | - A CI test is failing consistently on main (scheduled runs)
  12 | - You need to find which PR introduced a regression
  13 | - You suspect a runner-specific or GPU-specific issue
  14 | - You want to reproduce a CI failure on a remote server
  15 | 
  16 | ## Arguments
  17 | 
  18 | - **First argument (required)**: Test file name (e.g. `test_lora_tp.py`) or a GitHub Actions job URL
  19 | - **Second argument (optional)**: SSH target for remote reproduction (e.g. `user@host`)
  20 | - **Third argument (optional)**: Docker container name on the SSH target (e.g. `sglang_dev`)
  21 | 
  22 | If SSH target and docker container are not provided, the skill will only perform the CI log analysis and bisection, without remote reproduction. **Ask the user** for these if reproduction is needed and they weren't provided.
  23 | 
  24 | ## Background: Scheduled CI Runs
  25 | 
  26 | SGLang uses the `pr-test.yml` workflow with **scheduled runs** (cron-triggered) to periodically test the `main` branch. These runs are the primary data source for detecting regressions:
  27 | 
  28 | - **Workflow**: `pr-test.yml` with `event: schedule`
  29 | - **Branch**: `main`
  30 | - **Dashboard**: https://github.com/sgl-project/sglang/actions/workflows/pr-test.yml?query=event%3Aschedule
  31 | - **Frequency**: Runs multiple times daily, each pinned to the HEAD of `main` at trigger time
  32 | - **Purpose**: Catches regressions that slip through PR-level CI (e.g., interaction bugs between merged PRs, hardware-specific issues)
  33 | 
  34 | Always use these scheduled runs (not PR-triggered runs) when bisecting regressions on `main`. The `--event schedule` filter in `gh run list` ensures you only see these periodic main-branch runs.
  35 | 
  36 | ## Workflow
  37 | 
  38 | ### Phase 1: Extract the Failure Signature
  39 | 
  40 | 1. **Get the failing test details from CI logs.** If given a URL, fetch logs directly. If given a test name, find recent scheduled runs of `pr-test.yml` on `main` that failed:
  41 | 
  42 | ```bash
  43 | # List recent scheduled runs targeting main (the primary source of truth for regressions)
  44 | # These are cron-triggered runs visible at:
  45 | # https://github.com/sgl-project/sglang/actions/workflows/pr-test.yml?query=event%3Aschedule
  46 | gh run list --repo sgl-project/sglang --workflow="pr-test.yml" --event schedule --branch main --limit 20 --json databaseId,conclusion,createdAt,headSha
  47 | 
  48 | # Find the job containing the test
  49 | gh run view {RUN_ID} --repo sgl-project/sglang --json jobs --jq '.jobs[] | select(.conclusion == "failure") | {name, conclusion, databaseId}'
  50 | 
  51 | # Get the failure details
  52 | gh run view {RUN_ID} --repo sgl-project/sglang --job {JOB_ID} --log 2>&1 | grep -E -B 5 -A 30 "AssertionError|FAIL|Error|{TEST_NAME}"
  53 | ```
  54 | 
  55 | 2. **Record the failure signature:**
  56 |    - Exact error message and assertion
  57 |    - Affected test method name
  58 |    - Model/config involved
  59 |    - Numeric values (e.g., tolerance diffs, scores)
  60 |    - Whether the failure is deterministic (same values across runs)
  61 | 
  62 | ### Phase 2: Temporal Bisection
  63 | 
  64 | 3. **Find the boundary between passing and failing runs.** Walk through the scheduled run history (from the `pr-test.yml` schedule runs on `main`) to identify:
  65 |    - Last known PASSING run (sha + date)
  66 |    - First known FAILING run (sha + date)
  67 | 
  68 | ```bash
  69 | # For each scheduled run, check the specific partition/job status
  70 | gh run view {RUN_ID} --repo sgl-project/sglang --json jobs --jq '.jobs[] | select(.name == "{JOB_NAME}") | {conclusion, databaseId}'
  71 | 
  72 | # Verify a specific test passed or failed in a run
  73 | gh run view {RUN_ID} --repo sgl-project/sglang --job {JOB_ID} --log 2>&1 | grep -E "{TEST_NAME}|PASSED|FAILED|logprobs mismatch" | head -10
  74 | ```
  75 | 
  76 | 4. **List commits between the boundary:**
  77 | 
  78 | ```bash
  79 | git log --oneline {LAST_PASS_SHA}..{FIRST_FAIL_SHA}
  80 | ```
  81 | 
  82 | 5. **Filter for relevant commits** that touch files related to the failing test (model layers, kernels, test utilities, etc.):
  83 | 
  84 | ```bash
  85 | git log --oneline {LAST_PASS_SHA}..{FIRST_FAIL_SHA} -- {relevant_paths}
  86 | ```
  87 | 
  88 | ### Phase 3: Runner/Hardware Analysis
  89 | 
  90 | 6. **Check if the failure is runner-specific.** Extract the runner identity from each failing and passing run:
  91 | 
  92 | ```bash
  93 | # Get runner name and machine
  94 | gh run view {RUN_ID} --repo sgl-project/sglang --job {JOB_ID} --log 2>&1 | grep -E "Runner name|Machine name" | head -5
  95 | 
  96 | # Get GPU/driver info
  97 | gh run view {RUN_ID} --repo sgl-project/sglang --job {JOB_ID} --log 2>&1 | grep -i -E "NVIDIA-SMI|Driver Version|CUDA Version" | head -5
  98 | 
  99 | # Get package versions
 100 | gh run view {RUN_ID} --repo sgl-project/sglang --job {JOB_ID} --log 2>&1 | grep -E "sgl.kernel.*==|flashinfer.*==" | head -5
 101 | ```
 102 | 
 103 | 7. **Correlate runners with pass/fail outcomes.** Build a table:
 104 | 
 105 | | Run ID | Date | Runner | GPU Type | Driver | Result |
 106 | |--------|------|--------|----------|--------|--------|
 107 | 
 108 | If all failures map to a specific runner type/GPU and all passes map to another, the issue is **hardware-specific**, not a code regression.
 109 | 
 110 | ### Phase 4: Code Analysis
 111 | 
 112 | 8. **If a code regression is suspected** (failures not runner-specific), examine the candidate commits:
 113 |    - Read the changed files
 114 |    - Understand how the changes could affect the failing test
 115 |    - Look for prefill-vs-decode differences, TP-specific paths, kernel changes
 116 | 
 117 | 9. **If a hardware issue is suspected**, analyze:
 118 |    - Kernel compatibility (CUDA compute capability)
 119 |    - Driver version differences
 120 |    - All-reduce / NCCL behavior differences
 121 |    - CUDA graph capture differences across GPU architectures
 122 | 
 123 | ### Phase 5: Remote Reproduction (Optional)
 124 | 
 125 | Only if SSH target and docker container were provided.
 126 | 
 127 | 10. **Verify the remote environment:**
 128 | 
 129 | ```bash
 130 | ssh {SSH_TARGET} "docker exec {CONTAINER} nvidia-smi --query-gpu=name,driver_version --format=csv"
 131 | ssh {SSH_TARGET} "docker exec {CONTAINER} pip show sgl-kernel sglang flashinfer-python 2>&1 | grep -E 'Name:|Version:'"
 132 | ```
 133 | 
 134 | 11. **Ensure latest code is installed.** If the container is stale, update:
 135 | 
 136 | ```bash
 137 | # Try fetching latest main
 138 | ssh {SSH_TARGET} "docker exec {CONTAINER} bash -c 'cd /path/to/sglang && git fetch origin main && git checkout origin/main'"
 139 | # Or download and install from tarball if git auth fails
 140 | ssh {SSH_TARGET} "docker exec {CONTAINER} bash -c 'cd /tmp && curl -L https://github.com/sgl-project/sglang/archive/refs/heads/main.tar.gz | tar xz && cd sglang-main && pip install -e \"python[all]\"'"
 141 | # Reinstall (after git fetch)
 142 | ssh {SSH_TARGET} "docker exec {CONTAINER} bash -c 'cd /path/to/sglang && pip install -e \"python[all]\"'"
 143 | # Install test dependencies if needed
 144 | ssh {SSH_TARGET} "docker exec {CONTAINER} pip install peft rouge-score"
 145 | ```
 146 | 
 147 | 12. **Create a minimal reproduction script** that:
 148 |     - Uses `if __name__ == '__main__'` with `mp.set_start_method("spawn")`
 149 |     - Runs the specific failing test configuration
 150 |     - Prints key metrics (diffs, scores, outputs)
 151 |     - Exits with code 1 on failure
 152 | 
 153 | 13. **Copy and run the reproduction script:**
 154 | 
 155 | ```bash
 156 | scp /tmp/repro_script.py {SSH_TARGET}:/tmp/
 157 | ssh {SSH_TARGET} "docker cp /tmp/repro_script.py {CONTAINER}:/tmp/"
 158 | ssh {SSH_TARGET} "docker exec -e CUDA_VISIBLE_DEVICES=0,1 {CONTAINER} python3 /tmp/repro_script.py"
 159 | ```
 160 | 
 161 | 14. **Run control experiments** to isolate the variable:
 162 |     - If suspecting TP issue: run with TP=1 as control
 163 |     - If suspecting GPU issue: compare same code on different GPU
 164 |     - If suspecting a specific commit: test before/after that commit
 165 | 
 166 | ### Phase 6: Report
 167 | 
 168 | 15. **Produce a structured report:**
 169 | 
 170 | ```markdown
 171 | ## CI Regression Bisection Report
 172 | 
 173 | ### Failure Signature
 174 | - **Test**: {test_file}::{test_method}
 175 | - **Error**: {exact error message}
 176 | - **Key metrics**: {numeric values}
 177 | - **Deterministic**: Yes/No
 178 | 
 179 | ### Root Cause Classification
 180 | One of:
 181 | - **Code Regression**: PR #{number} introduced the bug
 182 | - **Hardware-Specific**: Fails on {GPU_TYPE}, passes on others
 183 | - **Environment Change**: New runner/driver/package version
 184 | - **Pre-existing Flakiness**: Intermittent, not a new regression
 185 | 
 186 | ### Evidence
 187 | | Condition | Result |
 188 | |-----------|--------|
 189 | | {condition1} | PASS/FAIL |
 190 | | {condition2} | PASS/FAIL |
 191 | 
 192 | ### Timeline
 193 | - {date}: Last known pass ({sha}, {runner})
 194 | - {date}: First known fail ({sha}, {runner})
 195 | - {date}: Confirmed reproduction on {server}
 196 | 
 197 | ### Recommended Fix
 198 | - **Short-term**: {workaround}
 199 | - **Long-term**: {proper fix}
 200 | ```
 201 | 
 202 | ## Key Patterns to Recognize
 203 | 
 204 | | Pattern | Diagnosis |
 205 | |---------|-----------|
 206 | | Same SHA passes on runner A, fails on runner B | Hardware/runner-specific |
 207 | | All runners fail after commit X | Code regression from commit X |
 208 | | Intermittent - same runner sometimes passes/fails | Flaky test or race condition |
 209 | | Prefill OK but decode fails | TP/all-reduce issue in decode path |
 210 | | Works with TP=1, fails with TP>1 | Tensor parallelism bug |
 211 | | Exact same numeric diff every time | Deterministic bug, not flakiness |
 212 | 
 213 | ## Important Notes
 214 | 
 215 | - **Always check runner identity** before concluding it's a code regression. Many "consistent" failures are actually runner-specific.
 216 | - **Test partition assignments change over time** as tests are added/removed. A test may move between partitions, landing on different runner types.
 217 | - **H200 runners** use `/root/actions-runner/` path and machine names like `gpu-h200-worker-*`. Non-H200 runners use `/public_sglang_ci/runner-*` paths.
 218 | - When running remote reproduction, use `run_in_background` for long-running tests and check output with `TaskOutput`.
 219 | - Container environments may be stale - always verify package versions match CI before drawing conclusions.
```


---
## .claude/skills/write-sglang-test/SKILL.md

```
   1 | ---
   2 | name: write-sglang-test
   3 | description: Guide for writing SGLang CI/UT tests. Covers CustomTestCase, CI registration, server fixtures, model selection, mock testing, and test placement. Always read test/README.md for the full CI layout, how to run tests, and extra tips. Use when creating new tests, adding CI test cases, writing unit tests, or when the user asks to add tests for SGLang features.
   4 | ---
   5 | 
   6 | # Writing SGLang CI / UT Tests
   7 | 
   8 | This skill covers **how to write and register tests**. For CI pipeline internals (stage ordering, fast-fail, gating, partitioning, debugging CI failures), see the [CI workflow guide](../ci-workflow-guide/SKILL.md).
   9 | 
  10 | ## Core Rules
  11 | 
  12 | 1. **Always use `CustomTestCase`** — never raw `unittest.TestCase`. It ensures `tearDownClass` runs even when `setUpClass` fails, preventing resource leaks in CI.
  13 | 2. **`tearDownClass` must be defensive** — use `hasattr`/null checks before accessing resources (e.g. `cls.process`) that `setUpClass` may not have finished allocating.
  14 | 3. **Place tests in `test/registered/<category>/`** — except JIT kernel tests and benchmarks, which live in `python/sglang/jit_kernel/tests/` and `python/sglang/jit_kernel/benchmark/` (nested subfolders are allowed)
  15 | 4. **Reuse server fixtures** — inherit from `DefaultServerBase` or write `setUpClass`/`tearDownClass` with `popen_launch_server`
  16 | 5. **Prefer mock over real server** — when testing logic that doesn't need a server / engine launch (middleware, request routing, config validation, argument parsing), use `unittest.mock.patch` / `MagicMock` and place tests in `test/registered/unit/`. Only launch a real server when the test genuinely needs inference results or server lifecycle behavior.
  17 | 
  18 | JIT kernel exception:
  19 | - If the task is adding or updating code under `python/sglang/jit_kernel/`, prefer the `add-jit-kernel` skill first.
  20 | - JIT kernel correctness tests use `python/sglang/jit_kernel/tests/**/test_*.py`.
  21 | - JIT kernel benchmarks use `python/sglang/jit_kernel/benchmark/**/bench_*.py`.
  22 | - Those files are still executed by `test/run_suite.py`, but through dedicated kernel suites rather than `test/registered/`.
  23 | 
  24 | ---
  25 | 
  26 | ## Model & Backend Selection
  27 | 
  28 | | Scenario | Model | CI Registration | Suite |
  29 | |----------|-------|-----------------|-------|
  30 | | **Unit tests** (no server / engine launch) | None | `register_cpu_ci` (prefer) or `register_cuda_ci` | `stage-a-test-cpu` or `stage-b-test-1-gpu-small` |
  31 | | **Common / backend-independent** (middleware, abort, routing, config, arg parsing) | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST` (1B) | `register_cuda_ci` only | `stage-b-test-1-gpu-small` |
  32 | | **Model-agnostic functionality** (sampling, session, OpenAI API features) | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST` (1B) | `register_cuda_ci` (+ AMD if relevant) | `stage-b-test-1-gpu-small` |
  33 | | **General performance** (single node, no spec/DP/parallelism) | `DEFAULT_MODEL_NAME_FOR_TEST` (8B) | `register_cuda_ci` | `stage-b-test-1-gpu-large` |
  34 | | **Bigger features** (spec, DP, TP, disaggregation) | Case by case | Case by case | See suite table below |
  35 | 
  36 | **Key principle for E2E tests**: Do NOT add `register_amd_ci` unless the test specifically exercises AMD/ROCm code paths. Common E2E tests just need any GPU to run — duplicating across backends wastes CI time with no extra coverage.
  37 | 
  38 | ### All model constants
  39 | 
  40 | Defined in `python/sglang/test/test_utils.py`:
  41 | 
  42 | | Constant | Model | When to use |
  43 | |----------|-------|-------------|
  44 | | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST` | Llama-3.2-1B-Instruct | Common features, model-agnostic tests |
  45 | | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST_BASE` | Llama-3.2-1B | Base (non-instruct) model tests |
  46 | | `DEFAULT_MODEL_NAME_FOR_TEST` | Llama-3.1-8B-Instruct | General performance (single node) |
  47 | | `DEFAULT_MOE_MODEL_NAME_FOR_TEST` | Mixtral-8x7B-Instruct | MoE-specific tests |
  48 | | `DEFAULT_SMALL_EMBEDDING_MODEL_NAME_FOR_TEST` | — | Embedding tests |
  49 | | `DEFAULT_SMALL_VLM_MODEL_NAME_FOR_TEST` | — | Vision-language tests |
  50 | 
  51 | ### Naming Conventions
  52 | 
  53 | - **Suite**: `stage-{a,b,c}-test-{gpu_count}-gpu-{hardware}` (e.g., `stage-b-test-1-gpu-small`)
  54 | - **CI runner**: `{gpu_count}-gpu-{hardware}` (e.g., `1-gpu-5090`, `4-gpu-h100`, `8-gpu-h200`)
  55 | 
  56 | ### All CI Suites
  57 | 
  58 | #### Per-commit (CUDA)
  59 | 
  60 | | Suite | Runner (label) | Description |
  61 | |-------|----------------|-------------|
  62 | | `stage-a-test-1-gpu-small` | `1-gpu-5090` | Quick checks on a small NVIDIA GPU before heavier stages |
  63 | | `stage-a-test-cpu` | `ubuntu-latest` | CPU-only unit tests |
  64 | | `stage-b-test-1-gpu-small` | `1-gpu-5090` | Core engine tests that fit a 5090-class card |
  65 | | `stage-b-test-1-gpu-large` | `1-gpu-h100` | Tests that need H100-class memory or kernels (e.g. FA3) |
  66 | | `stage-b-test-2-gpu-large` | `2-gpu-h100` | Two-GPU correctness and parallelism (TP/PP) on H100 |
  67 | | `stage-b-test-4-gpu-b200` | `4-gpu-b200` | Early Blackwell coverage (SM100+ paths) on four GPUs |
  68 | | `stage-b-kernel-unit-1-gpu-large` | `1-gpu-h100` | JIT kernel correctness tests under `python/sglang/jit_kernel/tests/` |
  69 | | `stage-b-kernel-unit-8-gpu-h200` | `8-gpu-h200` | Multi-GPU JIT kernel correctness tests under `python/sglang/jit_kernel/tests/` |
  70 | | `stage-b-kernel-benchmark-1-gpu-large` | `1-gpu-h100` | JIT kernel benchmark files under `python/sglang/jit_kernel/benchmark/` |
  71 | | `stage-c-test-4-gpu-h100` | `4-gpu-h100` | Large 4-GPU H100 integration and scaling tests |
  72 | | `stage-c-test-8-gpu-h200` | `8-gpu-h200` | Large 8-GPU H200 runs for big models and parallelism |
  73 | | `stage-c-test-8-gpu-h20` | `8-gpu-h20` | Large 8-GPU H20 runs for big models |
  74 | | `stage-c-test-deepep-4-gpu-h100` | `4-gpu-h100` | DeepEP expert-parallel and networking on four H100s |
  75 | | `stage-c-test-deepep-8-gpu-h200` | `8-gpu-h200` | DeepEP at 8-GPU H200 scale |
  76 | | `stage-c-test-8-gpu-b200` | `8-gpu-b200` | 8-GPU B200 suite (registered but not yet wired to a workflow) |
  77 | | `stage-c-test-4-gpu-b200` | `4-gpu-b200` | 4-GPU B200 suite for large models on Blackwell |
  78 | | `stage-c-test-4-gpu-gb200` | `4-gpu-gb200` | 4-GPU GB200 suite for large models on Grace Blackwell |
  79 | 
  80 | #### Per-commit (AMD)
  81 | 
  82 | | Suite | Runner (label) | Description |
  83 | |-------|----------------|-------------|
  84 | | `stage-a-test-1-gpu-small-amd` | `linux-mi325-1gpu-sglang` | Quick checks on one MI325-class GPU |
  85 | | `stage-b-test-1-gpu-small-amd` | `linux-mi325-1gpu-sglang` | Core 1-GPU AMD tests (14 partitions) |
  86 | | `stage-b-test-1-gpu-small-amd-nondeterministic` | `linux-mi325-1gpu-sglang` | Non-deterministic 1-GPU AMD tests |
  87 | | `stage-b-test-1-gpu-small-amd-mi35x` | `linux-mi35x-gpu-1` | 1-GPU tests on MI35x hardware |
  88 | | `stage-b-test-1-gpu-large-amd` | `linux-mi325-1gpu-sglang` | Large 1-GPU AMD tests (2 partitions) |
  89 | | `stage-b-test-2-gpu-large-amd` | `linux-mi325-2gpu-sglang` | 2-GPU ROCm correctness and parallel setups |
  90 | | `stage-b-test-large-8-gpu-35x-disaggregation-amd` | `linux-mi35x-gpu-8.fabric` | PD disaggregation and RDMA on 8×MI35x fabric |
  91 | | `stage-c-test-4-gpu-amd` | `linux-mi325-4gpu-sglang` | 4-GPU AMD integration (2 partitions) |
  92 | | `stage-c-test-large-8-gpu-amd` | `linux-mi325-8gpu-sglang` | 8-GPU MI325 scaling and integration |
  93 | | `stage-c-test-large-8-gpu-amd-mi35x` | `linux-mi35x-gpu-8` | 8-GPU MI35x scaling (2 partitions) |
  94 | 
  95 | #### Nightly
  96 | 
  97 | Nightly suites are listed in `NIGHTLY_SUITES` in [`test/run_suite.py`](../../../test/run_suite.py). They run via `nightly-test-nvidia.yml` and `nightly-test-amd.yml`, not `pr-test.yml`. Examples:
  98 | 
  99 | - `nightly-1-gpu` (CUDA)
 100 | - `nightly-kernel-1-gpu` (CUDA, JIT kernel full grids)
 101 | - `nightly-kernel-8-gpu-h200` (CUDA, multi-GPU JIT kernel nightly)
 102 | - `nightly-8-gpu-h200` (CUDA)
 103 | - `nightly-eval-vlm-2-gpu` (CUDA)
 104 | - `nightly-amd` (AMD)
 105 | - `nightly-amd-8-gpu-mi35x` (AMD)
 106 | 
 107 | > **Note**: Multimodal diffusion uses `python/sglang/multimodal_gen/test/run_suite.py`, not `test/run_suite.py`.
 108 | 
 109 | ### Choosing a Suite
 110 | 
 111 | Use the lightest suite that meets your test's needs:
 112 | 
 113 | - **No GPU required** → `stage-a-test-cpu`
 114 | - **Most small GPU tests** → `stage-b-test-1-gpu-small` (default choice)
 115 | - **Need H100 memory or Hopper features** → `stage-b-test-1-gpu-large`
 116 | - **JIT kernel correctness** → `stage-b-kernel-unit-1-gpu-large`
 117 | - **JIT kernel benchmarks** → `stage-b-kernel-benchmark-1-gpu-large`
 118 | - **Multi-GPU** → only when the test actually needs multiple GPUs
 119 | 
 120 | ---
 121 | 
 122 | ## Test File Templates
 123 | 
 124 | ### Unit Tests (no server / engine launch)
 125 | 
 126 | See `test/registered/unit/README.md` for quick-start and rules. Unit tests live in `test/registered/unit/`, mirroring `python/sglang/srt/`:
 127 | 
 128 | ```python
 129 | """Unit tests for srt/<module>"""
 130 | 
 131 | import unittest
 132 | from unittest.mock import MagicMock, patch
 133 | 
 134 | from sglang.srt.<module> import TargetClass
 135 | from sglang.test.ci.ci_register import register_cpu_ci
 136 | from sglang.test.test_utils import CustomTestCase
 137 | 
 138 | register_cpu_ci(est_time=5, suite="stage-a-test-cpu")
 139 | # Prefer CPU. Only use register_cuda_ci when the test truly needs a GPU.
 140 | 
 141 | class TestTargetClass(CustomTestCase):
 142 |     def test_basic_behavior(self):
 143 |         obj = TargetClass(...)
 144 |         self.assertEqual(obj.method(), expected)
 145 | 
 146 |     @patch("sglang.srt.<module>.some_dependency")
 147 |     def test_with_mock(self, mock_dep):
 148 |         mock_dep.return_value = MagicMock()
 149 |         # test logic with dependency mocked
 150 |         ...
 151 | 
 152 | 
 153 | if __name__ == "__main__":
 154 |     unittest.main()
 155 | ```
 156 | 
 157 | Use `unittest.mock.patch` / `MagicMock` to mock dependencies and isolate the logic under test. If the module fails to import on CPU CI (e.g., imports `torch` or CUDA ops at module level), use `sys.modules` stubs to make the import succeed. See existing tests in `test/registered/unit/` for examples.
 158 | 
 159 | **Quality bar** — test real logic (validation boundaries, state transitions, error paths, branching, etc.). Skip tests that just verify Python itself works (e.g., "does calling an abstract method raise `NotImplementedError`?", "does a dataclass store the field I assigned?"). Consolidate repetitive patterns into parameterized tests. No production code changes in test PRs.
 160 | 
 161 | ### E2E test (small model, server needed)
 162 | 
 163 | ```python
 164 | import unittest
 165 | 
 166 | import requests
 167 | 
 168 | from sglang.srt.utils import kill_process_tree
 169 | from sglang.test.ci.ci_register import register_cuda_ci
 170 | from sglang.test.test_utils import (
 171 |     DEFAULT_SMALL_MODEL_NAME_FOR_TEST,
 172 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
 173 |     DEFAULT_URL_FOR_TEST,
 174 |     CustomTestCase,
 175 |     popen_launch_server,
 176 | )
 177 | 
 178 | register_cuda_ci(est_time=60, suite="stage-b-test-1-gpu-small")
 179 | 
 180 | 
 181 | class TestMyFeature(CustomTestCase):
 182 |     @classmethod
 183 |     def setUpClass(cls):
 184 |         cls.model = DEFAULT_SMALL_MODEL_NAME_FOR_TEST
 185 |         cls.base_url = DEFAULT_URL_FOR_TEST
 186 |         cls.process = popen_launch_server(
 187 |             cls.model,
 188 |             cls.base_url,
 189 |             timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
 190 |             other_args=["--arg1", "value1"],  # feature-specific args
 191 |         )
 192 | 
 193 |     @classmethod
 194 |     def tearDownClass(cls):
 195 |         if hasattr(cls, "process") and cls.process:
 196 |             kill_process_tree(cls.process.pid)
 197 | 
 198 |     def test_basic_functionality(self):
 199 |         response = requests.post(
 200 |             self.base_url + "/generate",
 201 |             json={"text": "Hello", "sampling_params": {"max_new_tokens": 32}},
 202 |         )
 203 |         self.assertEqual(response.status_code, 200)
 204 | 
 205 | 
 206 | if __name__ == "__main__":
 207 |     unittest.main(verbosity=3)
 208 | ```
 209 | 
 210 | ### E2E test (8B model, server needed, performance)
 211 | 
 212 | ```python
 213 | import time
 214 | import unittest
 215 | 
 216 | import requests
 217 | 
 218 | from sglang.srt.utils import kill_process_tree
 219 | from sglang.test.ci.ci_register import register_cuda_ci
 220 | from sglang.test.test_utils import (
 221 |     DEFAULT_MODEL_NAME_FOR_TEST,
 222 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
 223 |     DEFAULT_URL_FOR_TEST,
 224 |     CustomTestCase,
 225 |     popen_launch_server,
 226 | )
 227 | 
 228 | register_cuda_ci(est_time=300, suite="stage-b-test-1-gpu-large")
 229 | 
 230 | 
 231 | class TestMyFeaturePerf(CustomTestCase):
 232 |     @classmethod
 233 |     def setUpClass(cls):
 234 |         cls.model = DEFAULT_MODEL_NAME_FOR_TEST
 235 |         cls.base_url = DEFAULT_URL_FOR_TEST
 236 |         cls.process = popen_launch_server(
 237 |             cls.model,
 238 |             cls.base_url,
 239 |             timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
 240 |         )
 241 | 
 242 |     @classmethod
 243 |     def tearDownClass(cls):
 244 |         if hasattr(cls, "process") and cls.process:
 245 |             kill_process_tree(cls.process.pid)
 246 | 
 247 |     def test_latency(self):
 248 |         start = time.perf_counter()
 249 |         response = requests.post(
 250 |             self.base_url + "/generate",
 251 |             json={"text": "Hello", "sampling_params": {"max_new_tokens": 128}},
 252 |         )
 253 |         elapsed = time.perf_counter() - start
 254 |         self.assertEqual(response.status_code, 200)
 255 |         self.assertLess(elapsed, 5.0, "Latency exceeded threshold")
 256 | 
 257 | 
 258 | if __name__ == "__main__":
 259 |     unittest.main(verbosity=3)
 260 | ```
 261 | 
 262 | ---
 263 | 
 264 | ## Server Fixture Reuse
 265 | 
 266 | For tests that only need a standard server, inherit from `DefaultServerBase` and override class attributes:
 267 | 
 268 | ```python
 269 | from sglang.test.server_fixtures.default_fixture import DefaultServerBase
 270 | 
 271 | class TestMyFeature(DefaultServerBase):
 272 |     model = DEFAULT_SMALL_MODEL_NAME_FOR_TEST
 273 |     other_args = ["--enable-my-feature"]
 274 | 
 275 |     def test_something(self):
 276 |         ...
 277 | ```
 278 | 
 279 | Available fixtures in `python/sglang/test/server_fixtures/`:
 280 | 
 281 | | Fixture | Use case |
 282 | |---------|----------|
 283 | | `DefaultServerBase` | Standard single-server tests |
 284 | | `EagleServerBase` | EAGLE speculative decoding |
 285 | | `PDDisaggregationServerBase` | Disaggregated prefill/decode |
 286 | | `MMMUServerBase` | Multimodal VLM tests |
 287 | 
 288 | ---
 289 | 
 290 | ## CI Registration
 291 | 
 292 | Every CI-discovered test file must call a registration function at module level:
 293 | 
 294 | ```python
 295 | from sglang.test.ci.ci_register import (
 296 |     register_cuda_ci,
 297 |     register_amd_ci,
 298 |     register_cpu_ci,
 299 |     register_npu_ci,
 300 | )
 301 | 
 302 | # Per-commit test (small 1-gpu, runs on 5090)
 303 | register_cuda_ci(est_time=80, suite="stage-b-test-1-gpu-small")
 304 | 
 305 | # Per-commit test (large 1-gpu, runs on H100)
 306 | register_cuda_ci(est_time=120, suite="stage-b-test-1-gpu-large")
 307 | 
 308 | # Nightly-only test
 309 | register_cuda_ci(est_time=200, suite="nightly-1-gpu", nightly=True)
 310 | 
 311 | # Multi-backend test (only when testing backend-specific code paths)
 312 | register_cuda_ci(est_time=80, suite="stage-a-test-1-gpu-small")
 313 | register_amd_ci(est_time=120, suite="stage-a-test-1-gpu-small-amd")
 314 | register_npu_ci(est_time=400, suite="nightly-8-npu-a3", nightly=True)
 315 | 
 316 | # Temporarily disabled test
 317 | register_cuda_ci(est_time=80, suite="stage-b-test-1-gpu-small", disabled="flaky - see #12345")
 318 | ```
 319 | 
 320 | Parameters:
 321 | - `est_time`: estimated runtime in seconds (used for CI partitioning)
 322 | - `suite`: which CI suite to run in (see suite tables above)
 323 | - `nightly=True`: for nightly-only tests (default `False` = per-commit)
 324 | - `disabled="reason"`: temporarily disable with explanation
 325 | 
 326 | **Key principle**: Only add `register_amd_ci` / `register_npu_ci` when the test exercises backend-specific code paths. Common E2E tests just need `register_cuda_ci` — duplicating across backends wastes CI time.
 327 | 
 328 | ### JIT Kernel Registration
 329 | 
 330 | JIT kernel files live outside `test/registered/` but still use registration:
 331 | 
 332 | ```python
 333 | from sglang.test.ci.ci_register import register_cuda_ci
 334 | 
 335 | # Correctness tests in python/sglang/jit_kernel/tests/
 336 | register_cuda_ci(est_time=30, suite="stage-b-kernel-unit-1-gpu-large")
 337 | register_cuda_ci(est_time=120, suite="stage-b-kernel-unit-8-gpu-h200")
 338 | 
 339 | # Benchmarks in python/sglang/jit_kernel/benchmark/
 340 | register_cuda_ci(est_time=6, suite="stage-b-kernel-benchmark-1-gpu-large")
 341 | 
 342 | # Optional nightly registration
 343 | register_cuda_ci(est_time=120, suite="nightly-kernel-1-gpu", nightly=True)
 344 | register_cuda_ci(est_time=120, suite="nightly-kernel-8-gpu-h200", nightly=True)
 345 | ```
 346 | 
 347 | Keep `est_time` and `suite` as **literal values** — `run_suite.py` collects them by AST parsing
 348 | 
 349 | ---
 350 | 
 351 | ## Test Placement
 352 | 
 353 | ```
 354 | test/
 355 | ├── registered/          # CI tests (auto-discovered by run_suite.py)
 356 | │   ├── unit/            # No server / engine launch (see test/registered/unit/README.md)
 357 | │   ├── kernels/         # CUDA kernel correctness (no server, GPU required)
 358 | │   ├── sampling/        # test_penalty.py, test_sampling_params.py ...
 359 | │   ├── sessions/        # test_session_control.py ...
 360 | │   ├── openai_server/   # basic/, features/, validation/ ...
 361 | │   ├── spec/            # eagle/, utils/ ...
 362 | │   ├── models/          # model-specific accuracy tests
 363 | │   ├── perf/            # performance benchmarks
 364 | │   └── <category>/      # create new category if needed
 365 | ├── manual/              # Non-CI: debugging, one-off, manual verification
 366 | └── run_suite.py         # CI runner (scans registered/ plus jit_kernel test/benchmark files)
 367 | 
 368 | python/sglang/jit_kernel/
 369 | ├── tests/               # JIT kernel correctness tests (CI-discovered by test/run_suite.py)
 370 | └── benchmark/           # JIT kernel benchmarks (CI-discovered by test/run_suite.py)
 371 | ```
 372 | 
 373 | **Decision rule** (see also `test/registered/README.md`):
 374 | - Component logic, no server → `registered/unit/`
 375 | - JIT kernel correctness / benchmarks → `python/sglang/jit_kernel/tests/` or `python/sglang/jit_kernel/benchmark/`
 376 | - Other kernel correctness → `registered/kernels/`
 377 | - Server needed → `registered/<category>/`
 378 | - Local debugging → `manual/`
 379 | 
 380 | ---
 381 | 
 382 | ## Eval Accuracy Mixins
 383 | 
 384 | **Design philosophy**: Most test files don't care about eval logic — they only need a "does this feature break model output quality?" sanity check. The mixin pattern separates **what to test** (threshold) from **how to test** (run_eval, assertions, CI summary). Test classes declare thresholds as class attributes; the mixin provides the `test_*` method. Override when you need extra assertions (e.g. EAGLE accept length).
 385 | 
 386 | Available mixins in `python/sglang/test/kits/eval_accuracy_kit.py`: `MMLUMixin`, `HumanEvalMixin`, `MGSMEnMixin`, `GSM8KMixin`. Can be combined freely. Read the source for attrs and defaults.
 387 | 
 388 | ```python
 389 | class TestMyFeature(CustomTestCase, MMLUMixin):
 390 |     mmlu_score_threshold = 0.65
 391 |     mmlu_num_examples = 64
 392 |     mmlu_num_threads = 32
 393 |     # test_mmlu is inherited — no code needed
 394 | ```
 395 | 
 396 | ---
 397 | 
 398 | ## Key Utilities
 399 | 
 400 | ```python
 401 | from sglang.test.test_utils import (
 402 |     CustomTestCase,              # base class with retry logic
 403 |     popen_launch_server,         # launch server subprocess
 404 |     DEFAULT_URL_FOR_TEST,        # auto-configured base URL
 405 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,  # 600s default
 406 |     run_bench_serving,           # benchmark helper (launch + bench)
 407 | )
 408 | from sglang.srt.utils import kill_process_tree  # cleanup server
 409 | ```
 410 | 
 411 | ---
 412 | 
 413 | ## Checklist
 414 | 
 415 | Before submitting a test:
 416 | 
 417 | - [ ] Inherits from `CustomTestCase` (not `unittest.TestCase`)
 418 | - [ ] Has `register_*_ci(...)` call at module level
 419 | - [ ] Placed in `test/registered/<category>/`, unless this is a JIT kernel test/benchmark
 420 | - [ ] JIT kernel work: files live in `python/sglang/jit_kernel/tests/` or `python/sglang/jit_kernel/benchmark/`
 421 | - [ ] Backend-independent tests: `register_cuda_ci` only + smallest model
 422 | - [ ] Logic that doesn't need a server / engine launch → unit test in `registered/unit/` (see Unit Tests section)
 423 | - [ ] `setUpClass` launches server, `tearDownClass` kills it (if server-based)
 424 | - [ ] `tearDownClass` is defensive — uses `hasattr`/null checks before accessing resources that may not have been allocated
 425 | - [ ] Has `if __name__ == "__main__": unittest.main()`
 426 | - [ ] `est_time` is reasonable (measure locally)
```


---
## README.md

```
   1 | <div align="center" id="sglangtop">
   2 | <img src="https://raw.githubusercontent.com/sgl-project/sglang/main/assets/logo.png" alt="logo" width="400" margin="10px"></img>
   3 | 
   4 | [![PyPI](https://img.shields.io/pypi/v/sglang)](https://pypi.org/project/sglang)
   5 | ![PyPI - Downloads](https://static.pepy.tech/badge/sglang?period=month)
   6 | [![license](https://img.shields.io/github/license/sgl-project/sglang.svg)](https://github.com/sgl-project/sglang/tree/main/LICENSE)
   7 | [![issue resolution](https://img.shields.io/github/issues-closed-raw/sgl-project/sglang)](https://github.com/sgl-project/sglang/issues)
   8 | [![open issues](https://img.shields.io/github/issues-raw/sgl-project/sglang)](https://github.com/sgl-project/sglang/issues)
   9 | [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sgl-project/sglang)
  10 | 
  11 | </div>
  12 | 
  13 | --------------------------------------------------------------------------------
  14 | 
  15 | <p align="center">
  16 | <a href="https://lmsys.org/blog/"><b>Blog</b></a> |
  17 | <a href="https://docs.sglang.io/"><b>Documentation</b></a> |
  18 | <a href="https://roadmap.sglang.io/"><b>Roadmap</b></a> |
  19 | <a href="https://slack.sglang.io/"><b>Join Slack</b></a> |
  20 | <a href="https://meet.sglang.io/"><b>Weekly Dev Meeting</b></a> |
  21 | <a href="https://github.com/sgl-project/sgl-learning-materials?tab=readme-ov-file#slides"><b>Slides</b></a>
  22 | </p>
  23 | 
  24 | ## News
  25 | - [2026/02] 🔥 Unlocking 25x Inference Performance with SGLang on NVIDIA GB300 NVL72 ([blog](https://lmsys.org/blog/2026-02-20-gb300-inferencex/)).
  26 | - [2026/01] 🔥 SGLang Diffusion accelerates video and image generation ([blog](https://lmsys.org/blog/2026-01-16-sglang-diffusion/)).
  27 | - [2025/12] SGLang provides day-0 support for latest open models ([MiMo-V2-Flash](https://lmsys.org/blog/2025-12-16-mimo-v2-flash/), [Nemotron 3 Nano](https://lmsys.org/blog/2025-12-15-run-nvidia-nemotron-3-nano/), [Mistral Large 3](https://github.com/sgl-project/sglang/pull/14213), [LLaDA 2.0 Diffusion LLM](https://lmsys.org/blog/2025-12-19-diffusion-llm/), [MiniMax M2](https://lmsys.org/blog/2025-11-04-miminmax-m2/)).
  28 | - [2025/10] 🔥 SGLang now runs natively on TPU with the SGLang-Jax backend ([blog](https://lmsys.org/blog/2025-10-29-sglang-jax/)).
  29 | - [2025/09] Deploying DeepSeek on GB200 NVL72 with PD and Large Scale EP (Part II): 3.8x Prefill, 4.8x Decode Throughput ([blog](https://lmsys.org/blog/2025-09-25-gb200-part-2/)).
  30 | - [2025/09] SGLang Day 0 Support for DeepSeek-V3.2 with Sparse Attention ([blog](https://lmsys.org/blog/2025-09-29-deepseek-V32/)).
  31 | - [2025/08] SGLang x AMD SF Meetup on 8/22: Hands-on GPU workshop, tech talks by AMD/xAI/SGLang, and networking ([Roadmap](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_sglang_roadmap.pdf), [Large-scale EP](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_sglang_ep.pdf), [Highlights](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_highlights.pdf), [AITER/MoRI](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_aiter_mori.pdf), [Wave](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_wave.pdf)).
  32 | 
  33 | <details>
  34 | <summary>More</summary>
  35 | 
  36 | - [2025/11] SGLang Diffusion accelerates video and image generation ([blog](https://lmsys.org/blog/2025-11-07-sglang-diffusion/)).
  37 | - [2025/10] PyTorch Conference 2025 SGLang Talk ([slide](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/sglang_pytorch_2025.pdf)).
  38 | - [2025/10] SGLang x Nvidia SF Meetup on 10/2 ([recap](https://x.com/lmsysorg/status/1975339501934510231)).
  39 | - [2025/08] SGLang provides day-0 support for OpenAI gpt-oss model ([instructions](https://github.com/sgl-project/sglang/issues/8833))
  40 | - [2025/06] SGLang, the high-performance serving infrastructure powering trillions of tokens daily, has been awarded the third batch of the Open Source AI Grant by a16z ([a16z blog](https://a16z.com/advancing-open-source-ai-through-benchmarks-and-bold-experimentation/)).
  41 | - [2025/05] Deploying DeepSeek with PD Disaggregation and Large-scale Expert Parallelism on 96 H100 GPUs ([blog](https://lmsys.org/blog/2025-05-05-large-scale-ep/)).
  42 | - [2025/06] Deploying DeepSeek on GB200 NVL72 with PD and Large Scale EP (Part I): 2.7x Higher Decoding Throughput ([blog](https://lmsys.org/blog/2025-06-16-gb200-part-1/)).
  43 | - [2025/03] Supercharge DeepSeek-R1 Inference on AMD Instinct MI300X ([AMD blog](https://rocm.blogs.amd.com/artificial-intelligence/DeepSeekR1-Part2/README.html))
  44 | - [2025/03] SGLang Joins PyTorch Ecosystem: Efficient LLM Serving Engine ([PyTorch blog](https://pytorch.org/blog/sglang-joins-pytorch/))
  45 | - [2025/02] Unlock DeepSeek-R1 Inference Performance on AMD Instinct™ MI300X GPU ([AMD blog](https://rocm.blogs.amd.com/artificial-intelligence/DeepSeekR1_Perf/README.html))
  46 | - [2025/01] SGLang provides day one support for DeepSeek V3/R1 models on NVIDIA and AMD GPUs with DeepSeek-specific optimizations. ([instructions](https://github.com/sgl-project/sglang/tree/main/benchmark/deepseek_v3), [AMD blog](https://www.amd.com/en/developer/resources/technical-articles/amd-instinct-gpus-power-deepseek-v3-revolutionizing-ai-development-with-sglang.html), [10+ other companies](https://x.com/lmsysorg/status/1887262321636221412))
  47 | - [2024/12] v0.4 Release: Zero-Overhead Batch Scheduler, Cache-Aware Load Balancer, Faster Structured Outputs ([blog](https://lmsys.org/blog/2024-12-04-sglang-v0-4/)).
  48 | - [2024/10] The First SGLang Online Meetup ([slides](https://github.com/sgl-project/sgl-learning-materials?tab=readme-ov-file#the-first-sglang-online-meetup)).
  49 | - [2024/09] v0.3 Release: 7x Faster DeepSeek MLA, 1.5x Faster torch.compile, Multi-Image/Video LLaVA-OneVision ([blog](https://lmsys.org/blog/2024-09-04-sglang-v0-3/)).
  50 | - [2024/07] v0.2 Release: Faster Llama3 Serving with SGLang Runtime (vs. TensorRT-LLM, vLLM) ([blog](https://lmsys.org/blog/2024-07-25-sglang-llama3/)).
  51 | - [2024/02] SGLang enables **3x faster JSON decoding** with compressed finite state machine ([blog](https://lmsys.org/blog/2024-02-05-compressed-fsm/)).
  52 | - [2024/01] SGLang provides up to **5x faster inference** with RadixAttention ([blog](https://lmsys.org/blog/2024-01-17-sglang/)).
  53 | - [2024/01] SGLang powers the serving of the official **LLaVA v1.6** release demo ([usage](https://github.com/haotian-liu/LLaVA?tab=readme-ov-file#demo)).
  54 | 
  55 | </details>
  56 | 
  57 | ## About
  58 | SGLang is a high-performance serving framework for large language models and multimodal models.
  59 | It is designed to deliver low-latency and high-throughput inference across a wide range of setups, from a single GPU to large distributed clusters.
  60 | Its core features include:
  61 | 
  62 | - **Fast Runtime**: Provides efficient serving with RadixAttention for prefix caching, a zero-overhead CPU scheduler, prefill-decode disaggregation, speculative decoding, continuous batching, paged attention, tensor/pipeline/expert/data parallelism, structured outputs, chunked prefill, quantization (FP4/FP8/INT4/AWQ/GPTQ), and multi-LoRA batching.
  63 | - **Broad Model Support**: Supports a wide range of language models (Llama, Qwen, DeepSeek, Kimi, GLM, GPT, Gemma, Mistral, etc.), embedding models (e5-mistral, gte, mcdse), reward models (Skywork), and diffusion models (WAN, Qwen-Image), with easy extensibility for adding new models. Compatible with most Hugging Face models and OpenAI APIs.
  64 | - **Extensive Hardware Support**: Runs on NVIDIA GPUs (GB200/B300/H100/A100/Spark/5090), AMD GPUs (MI355/MI300), Intel Xeon CPUs, Google TPUs, Ascend NPUs, and more.
  65 | - **Active Community**: SGLang is open-source and supported by a vibrant community with widespread industry adoption, powering over 400,000 GPUs worldwide.
  66 | - **RL & Post-Training Backbone**: SGLang is a proven rollout backend used for training many frontier models, with native RL integrations and adoption by well-known post-training frameworks such as [**AReaL**](https://github.com/inclusionAI/AReaL), [**Miles**](https://github.com/radixark/miles), [**slime**](https://github.com/THUDM/slime), [**Tunix**](https://github.com/google/tunix), [**verl**](https://github.com/volcengine/verl) and more.
  67 | 
  68 | ## Getting Started
  69 | - [Install SGLang](https://docs.sglang.io/get_started/install.html)
  70 | - [Quick Start](https://docs.sglang.io/basic_usage/send_request.html)
  71 | - [Backend Tutorial](https://docs.sglang.io/basic_usage/openai_api_completions.html)
  72 | - [Frontend Tutorial](https://docs.sglang.io/references/frontend/frontend_tutorial.html)
  73 | - [Contribution Guide](https://docs.sglang.io/developer_guide/contribution_guide.html)
  74 | 
  75 | ## Benchmark and Performance
  76 | Learn more in the release blogs: [v0.2 blog](https://lmsys.org/blog/2024-07-25-sglang-llama3/), [v0.3 blog](https://lmsys.org/blog/2024-09-04-sglang-v0-3/), [v0.4 blog](https://lmsys.org/blog/2024-12-04-sglang-v0-4/), [Large-scale expert parallelism](https://lmsys.org/blog/2025-05-05-large-scale-ep/), [GB200 rack-scale parallelism](https://lmsys.org/blog/2025-09-25-gb200-part-2/), [GB300 long context](https://lmsys.org/blog/2026-02-19-gb300-longctx/).
  77 | 
  78 | ## Adoption and Sponsorship
  79 | SGLang has been deployed at large scale, generating trillions of tokens in production each day. It is trusted and adopted by a wide range of leading enterprises and institutions, including xAI, AMD, NVIDIA, Intel, LinkedIn, Cursor, Oracle Cloud, Google Cloud, Microsoft Azure, AWS, Atlas Cloud, Voltage Park, Nebius, DataCrunch, Novita, InnoMatrix, MIT, UCLA, the University of Washington, Stanford, UC Berkeley, Tsinghua University, Jam & Tea Studios, Baseten, and other major technology organizations.
  80 | As an open-source LLM inference engine, SGLang has become the de facto industry standard, with deployments running on over 400,000 GPUs worldwide.
  81 | SGLang is currently hosted under the non-profit open-source organization [LMSYS](https://lmsys.org/about/).
  82 | 
  83 | <img src="https://raw.githubusercontent.com/sgl-project/sgl-learning-materials/refs/heads/main/slides/adoption.png" alt="logo" width="800" margin="10px"></img>
  84 | 
  85 | ## Contact Us
  86 | For enterprises interested in adopting or deploying SGLang at scale, including technical consulting, sponsorship opportunities, or partnership inquiries, please contact us at sglang@lmsys.org
  87 | 
  88 | ## Acknowledgment
  89 | We learned the design and reused code from the following projects: [Guidance](https://github.com/guidance-ai/guidance), [vLLM](https://github.com/vllm-project/vllm), [LightLLM](https://github.com/ModelTC/lightllm), [FlashInfer](https://github.com/flashinfer-ai/flashinfer), [Outlines](https://github.com/outlines-dev/outlines), and [LMQL](https://github.com/eth-sri/lmql).
```


---
## python/sglang/README.md

```
   1 | # Code Structure
   2 | 
   3 | - `eval`: The evaluation utilities.
   4 | - `lang`: The frontend language.
   5 | - `multimodal_gen`: Inference framework for accelerated image/video generation.
   6 | - `srt`: The backend engine for running local models. (SRT = SGLang Runtime).
   7 | - `test`: The test utilities.
   8 | - `api.py`: The public APIs.
   9 | - `bench_offline_throughput.py`: Benchmark the performance in the offline mode.
  10 | - `bench_one_batch.py`: Benchmark the latency of running a single static batch without a server.
  11 | - `bench_one_batch_server.py`: Benchmark the latency of running a single batch with a server.
  12 | - `bench_serving.py`: Benchmark online serving with dynamic requests.
  13 | - `check_env.py`: Check the environment variables and dependencies.
  14 | - `global_config.py`: The global configs and constants.
  15 | - `launch_server.py`: The entry point for launching a local server.
  16 | - `profiler.py`: The profiling entry point to send profile requests.
  17 | - `utils.py`: Common utilities.
  18 | - `version.py`: Version info.
```


---
## python/sglang/multimodal_gen/.claude/CLAUDE.md

```
   1 | # CLAUDE.md — sglang-diffusion (multimodal_gen)
   2 | 
   3 | ## What is this?
   4 | 
   5 | SGLang's diffusion/multimodal generation subsystem. Separate from the LLM runtime (`srt`). Supports 20+ image/video diffusion models (Wan, FLUX, HunyuanVideo, LTX, Qwen-Image, etc.) with distributed inference, LoRA, and multiple attention backends.
   6 | 
   7 | ## Quick Start
   8 | 
   9 | ```bash
  10 | # One-shot generation
  11 | sglang generate --model-path Wan-AI/Wan2.1-T2V-1.3B-Diffusers --prompt "A curious raccoon" --save-output
  12 | 
  13 | # Start server
  14 | sglang serve --model-path Wan-AI/Wan2.1-T2V-1.3B-Diffusers --num-gpus 4
  15 | 
  16 | # Python API
  17 | from sglang import DiffGenerator
  18 | gen = DiffGenerator.from_pretrained("Wan-AI/Wan2.1-T2V-1.3B-Diffusers")
  19 | result = gen.generate(sampling_params_kwargs={"prompt": "A curious raccoon"})
  20 | ```
  21 | 
  22 | ## Architecture
  23 | 
  24 | ```
  25 | CLI / Python API / HTTP Server (FastAPI + OpenAI-compatible)
  26 |     ↓ ZMQ
  27 | Scheduler (request queue, batching, dispatch)
  28 |     ↓ multiprocessing pipes
  29 | GPU Worker(s) → ComposedPipeline (stages: TextEncode → Denoise → Decode)
  30 | ```
  31 | 
  32 | ### Key Directories
  33 | 
  34 | ```
  35 | runtime/
  36 | ├── entrypoints/        # CLI (generate/serve), HTTP server, Python API (DiffGenerator)
  37 | ├── managers/           # scheduler.py, gpu_worker.py
  38 | ├── pipelines_core/     # ComposedPipelineBase, stages/, schedule_batch.py (Req/OutputBatch)
  39 | ├── pipelines/          # Model-specific pipelines (wan, flux, hunyuan, ltx, qwen_image, ...)
  40 | ├── models/             # encoders/, dits/, vaes/, schedulers/
  41 | ├── layers/             # attention/, lora/, quantization/
  42 | ├── loader/             # Model loading, weight utils
  43 | ├── server_args.py      # ServerArgs (all CLI/config params)
  44 | └── distributed/        # Multi-GPU (TP, SP: ulysses/ring)
  45 | configs/
  46 | ├── pipeline_configs/    # Per-model pipeline configs
  47 | ├── sample/             # SamplingParams
  48 | └── models/             # DiT, VAE, Encoder configs
  49 | ```
  50 | 
  51 | ### Key Classes
  52 | 
  53 | | Class | Location | Purpose |
  54 | |-------|----------|---------|
  55 | | `DiffGenerator` | `runtime/entrypoints/diffusion_generator.py` | Python API entry point |
  56 | | `ComposedPipelineBase` | `runtime/pipelines_core/composed_pipeline_base.py` | Pipeline orchestrator (stages) |
  57 | | `Scheduler` | `runtime/managers/scheduler.py` | ZMQ event loop, request dispatch |
  58 | | `GPUWorker` | `runtime/managers/gpu_worker.py` | GPU inference worker |
  59 | | `Req` / `OutputBatch` | `runtime/pipelines_core/schedule_batch.py` | Request/output containers |
  60 | | `ServerArgs` | `runtime/server_args.py` | All config params |
  61 | | `SamplingParams` | `configs/sample/sampling_params.py` | Generation params |
  62 | | `PipelineConfig` | `configs/pipeline_configs/base.py` | Model structure config |
  63 | 
  64 | ### Key Functions
  65 | 
  66 | | Function | Module | Purpose |
  67 | |----------|--------|---------|
  68 | | `build_pipeline()` | `runtime/pipelines_core/__init__.py` | Instantiate pipeline from model_path |
  69 | | `get_model_info()` | `registry.py` | Resolve pipeline + config classes |
  70 | | `launch_server()` | `runtime/launch_server.py` | Start multi-process server |
  71 | 
  72 | ## Adding a New Model
  73 | 
  74 | 1. Create pipeline in `runtime/pipelines/` extending `ComposedPipelineBase`
  75 | 2. Define stages via `create_pipeline_stages()` (TextEncoding → Denoising → Decoding)
  76 | 3. Add config in `configs/pipeline_configs/`
  77 | 4. Register in `registry.py` via `register_configs()`
  78 | 
  79 | ## Multi-GPU
  80 | 
  81 | ```bash
  82 | # Sequence parallelism (video frames across GPUs)
  83 | sglang serve --model-path ... --num-gpus 4 --ulysses-degree 2 --ring-degree 2
  84 | 
  85 | # Tensor parallelism (model layers across GPUs)
  86 | sglang serve --model-path ... --num-gpus 2 --tp-size 2
  87 | ```
  88 | 
  89 | ## Testing
  90 | 
  91 | ```bash
  92 | # Tests live in test/ subdirectory
  93 | python -m pytest python/sglang/multimodal_gen/test/
  94 | 
  95 | # No need to pre-download models — auto-downloaded at runtime
  96 | # Dependencies assumed already installed via `pip install -e "python[diffusion]"`
  97 | ```
  98 | 
  99 | ## Performance Tuning
 100 | 
 101 | For questions about optimal performance, fastest commands, VRAM reduction, or best flag combinations for a given model/GPU setup, **read the [sglang-diffusion-performance skill](skills/sglang-diffusion-performance/SKILL.md)**. It contains a complete table of lossless and lossy optimization flags with trade-offs, quick recipes, and tuning tips.
 102 | 
 103 | ### Perf Measurement
 104 | 
 105 | Look for `Pixel data generated successfully in xxxx seconds` in console output. With warmup enabled, use the line containing `warmup excluded` for accurate timing.
 106 | 
 107 | ## Env Vars
 108 | 
 109 | Defined in `envs.py` (300+ vars). Key ones:
 110 | - `SGLANG_DIFFUSION_ATTENTION_BACKEND` — attention backend override
 111 | - `SGLANG_CACHE_DIT_ENABLED` — enable Cache-DiT acceleration
 112 | - `SGLANG_CLOUD_STORAGE_TYPE` — cloud output storage (s3, etc.)
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-add-model/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-add-model
   3 | description: Use when adding a new diffusion model or Diffusers pipeline to SGLang.
   4 | ---
   5 | 
   6 | # Add a Diffusion Model to SGLang
   7 | 
   8 | Use this skill when adding a new diffusion model or pipeline variant to `sglang.multimodal_gen`.
   9 | 
  10 | ## Two Pipeline Styles
  11 | 
  12 | ### Style A: Hybrid Monolithic Pipeline (Recommended)
  13 | 
  14 | The recommended default for most new models. Uses a three-stage structure:
  15 | 
  16 | ```
  17 | BeforeDenoisingStage (model-specific)  -->  DenoisingStage (standard)  -->  DecodingStage (standard)
  18 | ```
  19 | 
  20 | - **BeforeDenoisingStage**: A single, model-specific stage that consolidates all pre-processing logic: input validation, text encoding, image encoding, latent preparation, timestep setup. This stage is unique per model.
  21 | - **DenoisingStage**: Framework-standard stage for the denoising loop (DiT/UNet forward passes). Shared across models.
  22 | - **DecodingStage**: Framework-standard stage for VAE decoding. Shared across models.
  23 | 
  24 | **Why recommended?** Modern diffusion models have highly heterogeneous pre-processing requirements (different text encoders, different latent formats, different conditioning mechanisms). The Hybrid approach keeps pre-processing isolated per model, avoids fragile shared stages with excessive conditional logic, and lets developers port Diffusers reference code quickly.
  25 | 
  26 | ### Style B: Modular Composition Style
  27 | 
  28 | Uses the framework's fine-grained standard stages (`TextEncodingStage`, `LatentPreparationStage`, `TimestepPreparationStage`, etc.) to build the pipeline by composition.
  29 | 
  30 | This style is appropriate when:
  31 | - **The new model's pre-processing can largely reuse existing stages** — e.g., a model that uses standard CLIP/T5 text encoding + standard latent preparation with minimal customization. In this case, `add_standard_t2i_stages()` or `add_standard_ti2i_stages()` may be all you need.
  32 | - **A model-specific optimization needs to be extracted as a standalone stage** — e.g., a specialized encoding or conditioning step that benefits from being a separate stage for profiling, parallelism control, or reuse across multiple pipeline variants.
  33 | 
  34 | See existing Modular examples: `QwenImagePipeline` (uses `add_standard_t2i_stages`), `FluxPipeline`, `WanPipeline`.
  35 | 
  36 | ### How to Choose
  37 | 
  38 | | Situation | Recommended Style |
  39 | |-----------|-------------------|
  40 | | Model has unique/complex pre-processing (VLM captioning, AR token generation, custom latent packing, etc.) | **Hybrid** — consolidate into a BeforeDenoisingStage |
  41 | | Model fits neatly into standard text-to-image or text+image-to-image pattern | **Modular** — use `add_standard_t2i_stages()` / `add_standard_ti2i_stages()` |
  42 | | Porting a Diffusers pipeline with many custom steps | **Hybrid** — copy the `__call__` logic into a single stage |
  43 | | Adding a variant of an existing model that shares most logic | **Modular** — reuse existing stages, customize via PipelineConfig callbacks |
  44 | | A specific pre-processing step needs special parallelism or profiling isolation | **Modular** — extract that step as a dedicated stage |
  45 | 
  46 | **Key principle (both styles)**: The stage(s) before `DenoisingStage` must produce a `Req` batch object with all the standard tensor fields that `DenoisingStage` expects (latents, timesteps, prompt_embeds, etc.). As long as this contract is met, the pipeline remains composable regardless of which style you use.
  47 | 
  48 | ---
  49 | 
  50 | ## Key Files and Directories
  51 | 
  52 | | Purpose | Path |
  53 | |---------|------|
  54 | | Pipeline classes | `python/sglang/multimodal_gen/runtime/pipelines/` |
  55 | | Model-specific stages | `python/sglang/multimodal_gen/runtime/pipelines_core/stages/model_specific_stages/` |
  56 | | PipelineStage base class | `python/sglang/multimodal_gen/runtime/pipelines_core/stages/base.py` |
  57 | | Pipeline base class | `python/sglang/multimodal_gen/runtime/pipelines_core/composed_pipeline_base.py` |
  58 | | Standard stages (Denoising, Decoding) | `python/sglang/multimodal_gen/runtime/pipelines_core/stages/` |
  59 | | Pipeline configs | `python/sglang/multimodal_gen/configs/pipeline_configs/` |
  60 | | Sampling params | `python/sglang/multimodal_gen/configs/sample/` |
  61 | | DiT model implementations | `python/sglang/multimodal_gen/runtime/models/dits/` |
  62 | | VAE implementations | `python/sglang/multimodal_gen/runtime/models/vaes/` |
  63 | | Encoder implementations | `python/sglang/multimodal_gen/runtime/models/encoders/` |
  64 | | Scheduler implementations | `python/sglang/multimodal_gen/runtime/models/schedulers/` |
  65 | | Model/VAE/DiT configs | `python/sglang/multimodal_gen/configs/models/dits/`, `vaes/`, `encoders/` |
  66 | | Central registry | `python/sglang/multimodal_gen/registry.py` |
  67 | 
  68 | ---
  69 | 
  70 | ## Step-by-Step Implementation
  71 | 
  72 | ### Step 1: Obtain and Study the Reference Implementation
  73 | 
  74 | **Before writing any code, obtain the model's reference implementation or Diffusers pipeline code.** You need the actual source code to work from — do not guess or assume the model's architecture. If the user already gave a HuggingFace model ID or repo, inspect that yourself first. Ask the user only when the reference implementation is private, ambiguous, or otherwise unavailable. Typical sources are:
  75 | - The model's Diffusers pipeline source (e.g., the `pipeline_*.py` file from the `diffusers` library or HuggingFace repo)
  76 | - Or the model's official reference implementation (e.g., from the model author's GitHub repo)
  77 | - Or the HuggingFace model ID so you can look up `model_index.json` and the associated pipeline class
  78 | 
  79 | Once you have the reference code, study it thoroughly:
  80 | 
  81 | 1. Find the model's `model_index.json` to identify required modules (text_encoder, vae, transformer, scheduler, etc.)
  82 | 2. Read the Diffusers pipeline's `__call__` method end-to-end. Identify:
  83 |    - How text prompts are encoded
  84 |    - How latents are prepared (shape, dtype, scaling)
  85 |    - How timesteps/sigmas are computed
  86 |    - What conditioning kwargs the DiT/UNet expects
  87 |    - How the denoising loop works (classifier-free guidance, etc.)
  88 |    - How VAE decoding is done (scaling factors, tiling, etc.)
  89 | 
  90 | ### Step 2: Evaluate Reuse of Existing Pipelines and Stages
  91 | 
  92 | **Before creating any new files, check whether an existing pipeline or stage can be reused or extended.** Only create new pipelines/stages when the existing ones would require extensive modifications or when no similar implementation exists.
  93 | 
  94 | Specifically:
  95 | 1. **Compare the new model's architecture against existing pipelines** (Flux, Wan, Qwen-Image, GLM-Image, HunyuanVideo, LTX, etc.). If the new model shares most of its structure with an existing one (e.g., same text encoders, similar latent format, compatible denoising loop), prefer:
  96 |    - Adding a new config variant to the existing pipeline rather than creating a new pipeline class
  97 |    - Reusing the existing `BeforeDenoisingStage` with minor parameter differences
  98 |    - Using `add_standard_t2i_stages()` / `add_standard_ti2i_stages()` / `add_standard_ti2v_stages()` if the model fits standard patterns
  99 | 2. **Check existing stages** in `runtime/pipelines_core/stages/` and `stages/model_specific_stages/`. If an existing stage handles 80%+ of what the new model needs, extend it rather than duplicating it.
 100 | 3. **Check existing model components** — many models share VAEs (e.g., `AutoencoderKL`), text encoders (CLIP, T5), and schedulers. Reuse these directly instead of re-implementing.
 101 | 
 102 | **Rule of thumb**: Only create a new file when the existing implementation would need substantial structural changes to accommodate the new model, or when no architecturally similar implementation exists.
 103 | 
 104 | ### Step 3: Implement Model Components
 105 | 
 106 | Adapt or implement the model's core components in the appropriate directories.
 107 | 
 108 | **DiT/Transformer** (`runtime/models/dits/{model_name}.py`):
 109 | 
 110 | ```python
 111 | # python/sglang/multimodal_gen/runtime/models/dits/my_model.py
 112 | 
 113 | import torch
 114 | import torch.nn as nn
 115 | 
 116 | from sglang.multimodal_gen.runtime.layers.layernorm import (
 117 |     LayerNormScaleShift,
 118 |     RMSNormScaleShift,
 119 | )
 120 | from sglang.multimodal_gen.runtime.layers.attention.selector import (
 121 |     get_attn_backend,
 122 | )
 123 | 
 124 | 
 125 | class MyModelTransformer2DModel(nn.Module):
 126 |     """DiT model for MyModel.
 127 | 
 128 |     Adapt from the Diffusers/reference implementation. Key points:
 129 |     - Use SGLang's fused LayerNorm/RMSNorm ops (see `existing-fast-paths.md` under the benchmark/profile skill)
 130 |     - Use SGLang's attention backend selector
 131 |     - Keep the same parameter naming as Diffusers for weight loading compatibility
 132 |     """
 133 | 
 134 |     def __init__(self, config):
 135 |         super().__init__()
 136 |         # ... model layers ...
 137 | 
 138 |     def forward(
 139 |         self,
 140 |         hidden_states: torch.Tensor,
 141 |         encoder_hidden_states: torch.Tensor,
 142 |         timestep: torch.Tensor,
 143 |         # ... model-specific kwargs ...
 144 |     ) -> torch.Tensor:
 145 |         # ... forward pass ...
 146 |         return output
 147 | ```
 148 | 
 149 | **Tensor Parallel (TP) and Sequence Parallel (SP)**: For multi-GPU deployment, it is recommended to add TP/SP support to the DiT model. This can be done incrementally after the single-GPU implementation is verified. Reference existing implementations and adapt to your model's architecture:
 150 | 
 151 | - **Wan model** (`runtime/models/dits/wanvideo.py`) — Full TP + SP reference:
 152 |   - TP: Uses `ColumnParallelLinear` for Q/K/V projections, `RowParallelLinear` for output projections, attention heads divided by `tp_size`
 153 |   - SP: Sequence dimension sharding via `get_sp_world_size()`, padding for alignment, `sequence_model_parallel_all_gather` for aggregation
 154 |   - Cross-attention skips SP (`skip_sequence_parallel=is_cross_attention`)
 155 | - **Qwen-Image model** (`runtime/models/dits/qwen_image.py`) — SP + USPAttention reference:
 156 |   - SP: Uses `USPAttention` (Ulysses + Ring Attention), configured via `--ulysses-degree` / `--ring-degree`
 157 |   - TP: Uses `MergedColumnParallelLinear` for QKV (with Nunchaku quantization), `ReplicatedLinear` otherwise
 158 | 
 159 | **Important**: These are references only — each model has its own architecture and parallelism requirements. Consider:
 160 | - How attention heads can be divided across TP ranks
 161 | - Whether the model's sequence dimension is naturally shardable for SP
 162 | - Which linear layers benefit from column/row parallel sharding vs. replication
 163 | - Whether cross-attention or other special modules need SP exclusion
 164 | 
 165 | Key imports for distributed support:
 166 | ```python
 167 | from sglang.multimodal_gen.runtime.distributed import (
 168 |     divide,
 169 |     get_sp_group,
 170 |     get_sp_world_size,
 171 |     get_tp_world_size,
 172 |     sequence_model_parallel_all_gather,
 173 | )
 174 | from sglang.multimodal_gen.runtime.layers.linear import (
 175 |     ColumnParallelLinear,
 176 |     RowParallelLinear,
 177 |     ReplicatedLinear,
 178 | )
 179 | ```
 180 | 
 181 | **VAE** (`runtime/models/vaes/{model_name}.py`): Implement if the model uses a non-standard VAE. Many models reuse existing VAEs.
 182 | 
 183 | **Encoders** (`runtime/models/encoders/{model_name}.py`): Implement if the model uses custom text/image encoders.
 184 | 
 185 | **Schedulers** (`runtime/models/schedulers/{scheduler_name}.py`): Implement if the model requires a custom scheduler not available in Diffusers.
 186 | 
 187 | ### Step 4: Create Model Configs
 188 | 
 189 | **DiT Config** (`configs/models/dits/{model_name}.py`):
 190 | 
 191 | ```python
 192 | # python/sglang/multimodal_gen/configs/models/dits/mymodel.py
 193 | 
 194 | from dataclasses import dataclass, field
 195 | 
 196 | from sglang.multimodal_gen.configs.models.dits.base import DiTConfig
 197 | 
 198 | 
 199 | @dataclass
 200 | class MyModelDitConfig(DiTConfig):
 201 |     arch_config: dict = field(default_factory=lambda: {
 202 |         "in_channels": 16,
 203 |         "num_layers": 24,
 204 |         "patch_size": 2,
 205 |         # ... model-specific architecture params ...
 206 |     })
 207 | ```
 208 | 
 209 | **VAE Config** (`configs/models/vaes/{model_name}.py`):
 210 | 
 211 | ```python
 212 | from dataclasses import dataclass, field
 213 | 
 214 | from sglang.multimodal_gen.configs.models.vaes.base import VAEConfig
 215 | 
 216 | 
 217 | @dataclass
 218 | class MyModelVAEConfig(VAEConfig):
 219 |     vae_scale_factor: int = 8
 220 |     # ... VAE-specific params ...
 221 | ```
 222 | 
 223 | **Sampling Params** (`configs/sample/{model_name}.py`):
 224 | 
 225 | ```python
 226 | from dataclasses import dataclass
 227 | 
 228 | from sglang.multimodal_gen.configs.sample.base import SamplingParams
 229 | 
 230 | 
 231 | @dataclass
 232 | class MyModelSamplingParams(SamplingParams):
 233 |     num_inference_steps: int = 50
 234 |     guidance_scale: float = 7.5
 235 |     height: int = 1024
 236 |     width: int = 1024
 237 |     # ... model-specific defaults ...
 238 | ```
 239 | 
 240 | ### Step 5: Create PipelineConfig
 241 | 
 242 | The `PipelineConfig` holds static model configuration and defines callback methods used by the standard `DenoisingStage` and `DecodingStage`.
 243 | 
 244 | ```python
 245 | # python/sglang/multimodal_gen/configs/pipeline_configs/my_model.py
 246 | 
 247 | from dataclasses import dataclass, field
 248 | 
 249 | from sglang.multimodal_gen.configs.pipeline_configs.base import (
 250 |     ImagePipelineConfig,      # for image generation
 251 |     # SpatialImagePipelineConfig,  # alternative base
 252 |     # VideoPipelineConfig,         # for video generation
 253 | )
 254 | from sglang.multimodal_gen.configs.models.dits.mymodel import MyModelDitConfig
 255 | from sglang.multimodal_gen.configs.models.vaes.mymodel import MyModelVAEConfig
 256 | 
 257 | 
 258 | @dataclass
 259 | class MyModelPipelineConfig(ImagePipelineConfig):
 260 |     """Pipeline config for MyModel.
 261 | 
 262 |     This config provides callbacks that the standard DenoisingStage and
 263 |     DecodingStage use during execution. The BeforeDenoisingStage handles
 264 |     all model-specific pre-processing independently.
 265 |     """
 266 | 
 267 |     task_type: ModelTaskType = ModelTaskType.T2I
 268 |     vae_precision: str = "bf16"
 269 |     should_use_guidance: bool = True
 270 |     vae_tiling: bool = False
 271 |     enable_autocast: bool = False
 272 | 
 273 |     dit_config: DiTConfig = field(default_factory=MyModelDitConfig)
 274 |     vae_config: VAEConfig = field(default_factory=MyModelVAEConfig)
 275 | 
 276 |     # --- Callbacks used by DenoisingStage ---
 277 | 
 278 |     def get_freqs_cis(self, batch, device, rotary_emb, dtype):
 279 |         """Prepare rotary position embeddings for the DiT."""
 280 |         # Model-specific RoPE computation
 281 |         ...
 282 |         return freqs_cis
 283 | 
 284 |     def prepare_pos_cond_kwargs(self, batch, latent_model_input, t, **kwargs):
 285 |         """Build positive conditioning kwargs for each denoising step."""
 286 |         return {
 287 |             "hidden_states": latent_model_input,
 288 |             "encoder_hidden_states": batch.prompt_embeds[0],
 289 |             "timestep": t,
 290 |             # ... model-specific kwargs ...
 291 |         }
 292 | 
 293 |     def prepare_neg_cond_kwargs(self, batch, latent_model_input, t, **kwargs):
 294 |         """Build negative conditioning kwargs for CFG."""
 295 |         return {
 296 |             "hidden_states": latent_model_input,
 297 |             "encoder_hidden_states": batch.negative_prompt_embeds[0],
 298 |             "timestep": t,
 299 |             # ... model-specific kwargs ...
 300 |         }
 301 | 
 302 |     # --- Callbacks used by DecodingStage ---
 303 | 
 304 |     def get_decode_scale_and_shift(self):
 305 |         """Return (scale, shift) for latent denormalization before VAE decode."""
 306 |         return self.vae_config.latents_std, self.vae_config.latents_mean
 307 | 
 308 |     def post_denoising_loop(self, latents, batch):
 309 |         """Optional post-processing after the denoising loop finishes."""
 310 |         return latents.to(torch.bfloat16)
 311 | 
 312 |     def post_decoding(self, frames, server_args):
 313 |         """Optional post-processing after VAE decoding."""
 314 |         return frames
 315 | ```
 316 | 
 317 | **Important**: The `prepare_pos_cond_kwargs` / `prepare_neg_cond_kwargs` methods define what the DiT receives at each denoising step. These must match the DiT's `forward()` signature.
 318 | 
 319 | ### Step 6: Implement the BeforeDenoisingStage (Core Step)
 320 | 
 321 | This is the heart of the Hybrid pattern. Create a single stage that handles ALL pre-processing.
 322 | 
 323 | ```python
 324 | # python/sglang/multimodal_gen/runtime/pipelines_core/stages/model_specific_stages/my_model.py
 325 | 
 326 | import torch
 327 | from typing import List, Optional, Union
 328 | 
 329 | from sglang.multimodal_gen.runtime.pipelines_core.schedule_batch import Req
 330 | from sglang.multimodal_gen.runtime.pipelines_core.stages.base import PipelineStage
 331 | from sglang.multimodal_gen.runtime.server_args import ServerArgs
 332 | from sglang.multimodal_gen.runtime.distributed import get_local_torch_device
 333 | from sglang.multimodal_gen.runtime.utils.logging_utils import init_logger
 334 | 
 335 | logger = init_logger(__name__)
 336 | 
 337 | 
 338 | class MyModelBeforeDenoisingStage(PipelineStage):
 339 |     """Monolithic pre-processing stage for MyModel.
 340 | 
 341 |     Consolidates all logic before the denoising loop:
 342 |     - Input validation
 343 |     - Text/image encoding
 344 |     - Latent preparation
 345 |     - Timestep/sigma computation
 346 | 
 347 |     This stage produces a Req batch with all fields required by
 348 |     the standard DenoisingStage.
 349 |     """
 350 | 
 351 |     def __init__(self, vae, text_encoder, tokenizer, transformer, scheduler):
 352 |         super().__init__()
 353 |         self.vae = vae
 354 |         self.text_encoder = text_encoder
 355 |         self.tokenizer = tokenizer
 356 |         self.transformer = transformer
 357 |         self.scheduler = scheduler
 358 |         # ... other initialization (image processors, scale factors, etc.) ...
 359 | 
 360 |     # --- Internal helper methods ---
 361 |     # Copy/adapt directly from the Diffusers reference pipeline.
 362 |     # These are private to this stage; no need to make them reusable.
 363 | 
 364 |     def _encode_prompt(self, prompt, device, dtype):
 365 |         """Encode text prompt into embeddings."""
 366 |         # ... model-specific text encoding logic ...
 367 |         return prompt_embeds, negative_prompt_embeds
 368 | 
 369 |     def _prepare_latents(self, batch_size, height, width, dtype, device, generator):
 370 |         """Create initial noisy latents."""
 371 |         # ... model-specific latent preparation ...
 372 |         return latents
 373 | 
 374 |     def _prepare_timesteps(self, num_inference_steps, device):
 375 |         """Compute the timestep/sigma schedule."""
 376 |         # ... model-specific timestep computation ...
 377 |         return timesteps, sigmas
 378 | 
 379 |     # --- Main forward method ---
 380 | 
 381 |     @torch.no_grad()
 382 |     def forward(self, batch: Req, server_args: ServerArgs) -> Req:
 383 |         """Execute all pre-processing and populate batch for DenoisingStage.
 384 | 
 385 |         This method mirrors the first half of a Diffusers pipeline __call__,
 386 |         up to (but not including) the denoising loop.
 387 |         """
 388 |         device = get_local_torch_device()
 389 |         dtype = torch.bfloat16
 390 |         generator = torch.Generator(device=device).manual_seed(batch.seed)
 391 | 
 392 |         # 1. Encode prompt
 393 |         prompt_embeds, negative_prompt_embeds = self._encode_prompt(
 394 |             batch.prompt, device, dtype
 395 |         )
 396 | 
 397 |         # 2. Prepare latents
 398 |         latents = self._prepare_latents(
 399 |             batch_size=1,
 400 |             height=batch.height,
 401 |             width=batch.width,
 402 |             dtype=dtype,
 403 |             device=device,
 404 |             generator=generator,
 405 |         )
 406 | 
 407 |         # 3. Prepare timesteps
 408 |         timesteps, sigmas = self._prepare_timesteps(
 409 |             batch.num_inference_steps, device
 410 |         )
 411 | 
 412 |         # 4. Populate batch with everything DenoisingStage needs
 413 |         batch.prompt_embeds = [prompt_embeds]
 414 |         batch.negative_prompt_embeds = [negative_prompt_embeds]
 415 |         batch.latents = latents
 416 |         batch.timesteps = timesteps
 417 |         batch.num_inference_steps = len(timesteps)
 418 |         batch.sigmas = sigmas
 419 |         batch.generator = generator
 420 |         batch.raw_latent_shape = latents.shape
 421 |         batch.height = batch.height
 422 |         batch.width = batch.width
 423 | 
 424 |         return batch
 425 | ```
 426 | 
 427 | **Key fields that `DenoisingStage` expects on the batch** (set these in your `forward`):
 428 | 
 429 | | Field | Type | Description |
 430 | |-------|------|-------------|
 431 | | `batch.latents` | `torch.Tensor` | Initial noisy latent tensor |
 432 | | `batch.timesteps` | `torch.Tensor` | Timestep schedule |
 433 | | `batch.num_inference_steps` | `int` | Number of denoising steps |
 434 | | `batch.sigmas` | `list[float]` | Sigma schedule (as a list, not numpy) |
 435 | | `batch.prompt_embeds` | `list[torch.Tensor]` | Positive prompt embeddings (wrapped in list) |
 436 | | `batch.negative_prompt_embeds` | `list[torch.Tensor]` | Negative prompt embeddings (wrapped in list) |
 437 | | `batch.generator` | `torch.Generator` | RNG generator for reproducibility |
 438 | | `batch.raw_latent_shape` | `tuple` | Original latent shape before any packing |
 439 | | `batch.height` / `batch.width` | `int` | Output dimensions |
 440 | 
 441 | ### Step 7: Define the Pipeline Class
 442 | 
 443 | The pipeline class is minimal -- it just wires the stages together.
 444 | 
 445 | ```python
 446 | # python/sglang/multimodal_gen/runtime/pipelines/my_model.py
 447 | 
 448 | from sglang.multimodal_gen.runtime.pipelines_core import LoRAPipeline
 449 | from sglang.multimodal_gen.runtime.pipelines_core.composed_pipeline_base import (
 450 |     ComposedPipelineBase,
 451 | )
 452 | from sglang.multimodal_gen.runtime.pipelines_core.stages import DenoisingStage
 453 | from sglang.multimodal_gen.runtime.pipelines_core.stages.model_specific_stages.my_model import (
 454 |     MyModelBeforeDenoisingStage,
 455 | )
 456 | from sglang.multimodal_gen.runtime.server_args import ServerArgs
 457 | 
 458 | 
 459 | class MyModelPipeline(LoRAPipeline, ComposedPipelineBase):
 460 |     pipeline_name = "MyModelPipeline"  # Must match model_index.json _class_name
 461 | 
 462 |     _required_config_modules = [
 463 |         "text_encoder",
 464 |         "tokenizer",
 465 |         "vae",
 466 |         "transformer",
 467 |         "scheduler",
 468 |         # ... list all modules from model_index.json ...
 469 |     ]
 470 | 
 471 |     def create_pipeline_stages(self, server_args: ServerArgs):
 472 |         # 1. Monolithic pre-processing (model-specific)
 473 |         self.add_stage(
 474 |             MyModelBeforeDenoisingStage(
 475 |                 vae=self.get_module("vae"),
 476 |                 text_encoder=self.get_module("text_encoder"),
 477 |                 tokenizer=self.get_module("tokenizer"),
 478 |                 transformer=self.get_module("transformer"),
 479 |                 scheduler=self.get_module("scheduler"),
 480 |             ),
 481 |         )
 482 | 
 483 |         # 2. Standard denoising loop (framework-provided)
 484 |         self.add_stage(
 485 |             DenoisingStage(
 486 |                 transformer=self.get_module("transformer"),
 487 |                 scheduler=self.get_module("scheduler"),
 488 |             ),
 489 |         )
 490 | 
 491 |         # 3. Standard VAE decoding (framework-provided)
 492 |         self.add_standard_decoding_stage()
 493 | 
 494 | 
 495 | # REQUIRED: This is how the registry discovers the pipeline
 496 | EntryClass = [MyModelPipeline]
 497 | ```
 498 | 
 499 | ### Step 8: Register the Model
 500 | 
 501 | In `python/sglang/multimodal_gen/registry.py`, register your configs:
 502 | 
 503 | ```python
 504 | register_configs(
 505 |     model_family="my_model",
 506 |     sampling_param_cls=MyModelSamplingParams,
 507 |     pipeline_config_cls=MyModelPipelineConfig,
 508 |     hf_model_paths=[
 509 |         "org/my-model-name",  # HuggingFace model ID(s)
 510 |     ],
 511 | )
 512 | ```
 513 | 
 514 | The `EntryClass` in your pipeline file is automatically discovered by the registry's `_discover_and_register_pipelines()` function -- no additional registration needed for the pipeline class itself.
 515 | 
 516 | ### Step 9: Verify Output Quality
 517 | 
 518 | After implementation, **you must verify that the generated output is not noise**. A noisy or garbled output image/video is the most common sign of an incorrect implementation. Common causes include:
 519 | 
 520 | - Incorrect latent scale/shift factors (`get_decode_scale_and_shift` returning wrong values)
 521 | - Wrong timestep/sigma schedule (order, dtype, or value range)
 522 | - Mismatched conditioning kwargs (fields not matching the DiT's `forward()` signature)
 523 | - Incorrect VAE decoder configuration (wrong `vae_scale_factor`, missing denormalization)
 524 | - Rotary embedding style mismatch (`is_neox_style` set incorrectly)
 525 | - Wrong prompt embedding format (missing list wrapping, wrong encoder output selection)
 526 | 
 527 | **If the output is noise, the implementation is incorrect — do not ship it.** Debug by:
 528 | 1. Comparing intermediate tensor values (latents, prompt_embeds, timesteps) against the Diffusers reference pipeline
 529 | 2. Running the Diffusers pipeline and SGLang pipeline side-by-side with the same seed
 530 | 3. Checking each stage's output shape and value range independently
 531 | 
 532 | ## Reference Implementations
 533 | 
 534 | ### Hybrid Style (recommended for most new models)
 535 | 
 536 | | Model | Pipeline | BeforeDenoisingStage | PipelineConfig |
 537 | |-------|----------|---------------------|----------------|
 538 | | GLM-Image | `runtime/pipelines/glm_image.py` | `stages/model_specific_stages/glm_image.py` | `configs/pipeline_configs/glm_image.py` |
 539 | | Qwen-Image-Layered | `runtime/pipelines/qwen_image.py` (`QwenImageLayeredPipeline`) | `stages/model_specific_stages/qwen_image_layered.py` | `configs/pipeline_configs/qwen_image.py` (`QwenImageLayeredPipelineConfig`) |
 540 | 
 541 | ### Modular Style (when standard stages fit well)
 542 | 
 543 | | Model | Pipeline | Notes |
 544 | |-------|----------|-------|
 545 | | Qwen-Image (T2I) | `runtime/pipelines/qwen_image.py` | Uses `add_standard_t2i_stages()` — standard text encoding + latent prep fits this model |
 546 | | Qwen-Image-Edit | `runtime/pipelines/qwen_image.py` | Uses `add_standard_ti2i_stages()` — standard image-to-image flow |
 547 | | Flux | `runtime/pipelines/flux.py` | Uses `add_standard_t2i_stages()` with custom `prepare_mu` |
 548 | | Wan | `runtime/pipelines/wan_pipeline.py` | Uses `add_standard_ti2v_stages()` |
 549 | 
 550 | ---
 551 | 
 552 | ## Checklist
 553 | 
 554 | Before submitting, verify:
 555 | 
 556 | **Common (both styles):**
 557 | - [ ] **Pipeline file** exists at `runtime/pipelines/{model_name}.py` with `EntryClass`
 558 | - [ ] **PipelineConfig** at `configs/pipeline_configs/{model_name}.py`
 559 | - [ ] **SamplingParams** at `configs/sample/{model_name}.py`
 560 | - [ ] **DiT model** at `runtime/models/dits/{model_name}.py`
 561 | - [ ] **DiT config** at `configs/models/dits/{model_name}.py`
 562 | - [ ] **VAE** — reuse existing (e.g., `AutoencoderKL`) or create new at `runtime/models/vaes/`
 563 | - [ ] **VAE config** — reuse existing or create new at `configs/models/vaes/{model_name}.py`
 564 | - [ ] **Registry entry** in `registry.py` via `register_configs()`
 565 | - [ ] `pipeline_name` matches Diffusers `model_index.json` `_class_name`
 566 | - [ ] `_required_config_modules` lists all modules from `model_index.json`
 567 | - [ ] `PipelineConfig` callbacks (`prepare_pos_cond_kwargs`, `get_freqs_cis`, etc.) match DiT's `forward()` signature
 568 | - [ ] Latent scale/shift factors are correctly configured
 569 | - [ ] Use fused kernels where possible (see `existing-fast-paths.md` under the benchmark/profile skill)
 570 | - [ ] Weight names match Diffusers for automatic loading
 571 | - [ ] **TP/SP support** considered for DiT model (recommended; reference `wanvideo.py` for TP+SP, `qwen_image.py` for USPAttention)
 572 | - [ ] **Output quality verified** — generated images/videos are not noise; compared against Diffusers reference output
 573 | 
 574 | **Hybrid style only:**
 575 | - [ ] **BeforeDenoisingStage** at `stages/model_specific_stages/{model_name}.py`
 576 | - [ ] `BeforeDenoisingStage.forward()` populates all fields needed by `DenoisingStage`
 577 | 
 578 | ## Common Pitfalls
 579 | 
 580 | 1. **`batch.sigmas` must be a Python list**, not a numpy array. Use `.tolist()` to convert.
 581 | 2. **`batch.prompt_embeds` is a list of tensors** (one per encoder), not a single tensor. Wrap with `[tensor]`.
 582 | 3. **Don't forget `batch.raw_latent_shape`** -- `DecodingStage` uses it to unpack latents.
 583 | 4. **Rotary embedding style matters**: `is_neox_style=True` = split-half rotation, `is_neox_style=False` = interleaved. Check the reference model carefully.
 584 | 5. **VAE precision**: Many VAEs need fp32 or bf16 for numerical stability. Set `vae_precision` in the PipelineConfig accordingly.
 585 | 6. **Avoid forcing model-specific logic into shared stages**: If your model's pre-processing doesn't naturally fit the existing standard stages, prefer the Hybrid pattern with a dedicated BeforeDenoisingStage rather than adding conditional branches to shared stages.
 586 | 
 587 | ## After Implementation: Tests and Performance Data
 588 | 
 589 | Once the model is working and output quality is verified, **ask the user** whether they would like to:
 590 | 
 591 | 1. **Add tests** — Create unit tests and/or integration tests for the new model. Tests should cover:
 592 |    - Pipeline construction and stage wiring
 593 |    - Single-GPU inference producing non-noise output
 594 |    - Multi-GPU inference (TP/SP) if supported
 595 |    - See the `write-sglang-test` skill for test conventions and placement guidelines
 596 | 
 597 | 2. **Generate performance data** — Run benchmarks and collect perf metrics:
 598 |    - Single-GPU latency and throughput (look for `Pixel data generated successfully in xxxx seconds` in console output; use the `warmup excluded` line for accurate timing)
 599 |    - Multi-GPU scaling (TP/SP) throughput comparison
 600 |    - Use `python/sglang/multimodal_gen/benchmarks/bench_serving.py` for serving benchmarks
 601 | 
 602 | Do not skip this step — always ask the user before proceeding, as test and benchmark requirements vary per model.
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-ako4all-kernel/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-ako4all-kernel
   3 | description: Use when optimizing an existing SGLang diffusion kernel with AKO4ALL, including AKO4ALL repo hygiene, custom microbench setup, ncu-guided iteration, and end-to-end denoise validation. Also use when a sibling AKO4ALL repo must be cloned or refreshed before starting kernel tuning work.
   4 | ---
   5 | 
   6 | # SGLang Diffusion AKO4ALL Kernel
   7 | 
   8 | Use this skill to run the full AKO4ALL-based optimization loop for an existing SGLang diffusion kernel.
   9 | It packages the workflow we used for diffusion Triton and JIT kernel tuning: bootstrap a custom AKO harness, benchmark and profile the kernel, iterate with `ncu`, port the best version back to `sglang`, then validate with targeted tests and model-level denoise runs.
  10 | 
  11 | This skill assumes a sibling repo layout like:
  12 | 
  13 | ```text
  14 | <base-dir>/
  15 | ├── sglang/
  16 | └── AKO4ALL/
  17 | ```
  18 | 
  19 | If `AKO4ALL/` is missing under the current base directory, clone it first.
  20 | 
  21 | ## Use This Skill When
  22 | 
  23 | - tuning an existing diffusion Triton, CUDA JIT, CuTeDSL, or runtime-integrated kernel in `sglang`
  24 | - creating a custom AKO4ALL harness for a real diffusion kernel instead of using the default benchmark tasks
  25 | - validating that a kernel-level win transfers to Qwen, FLUX, Wan, Hunyuan, MOVA, or other diffusion denoise latency
  26 | - preparing PR artifacts such as microbench tables, `ncu` before/after data, and proof image outputs
  27 | 
  28 | Do not use this skill when adding a brand-new kernel from scratch with no existing SGLang integration.
  29 | For that, start from the sibling kernel-authoring skills first:
  30 | 
  31 | - Triton: [../sglang-diffusion-triton-kernel/SKILL.md](../sglang-diffusion-triton-kernel/SKILL.md)
  32 | - CUDA JIT: [../sglang-diffusion-cuda-kernel/SKILL.md](../sglang-diffusion-cuda-kernel/SKILL.md)
  33 | - Denoise benchmark/profile: [../sglang-diffusion-benchmark-profile/SKILL.md](../sglang-diffusion-benchmark-profile/SKILL.md)
  34 | 
  35 | ## Mandatory AKO4ALL Preflight
  36 | 
  37 | Before any AKO work:
  38 | 
  39 | 1. Run `scripts/ensure_ako4all_clean.sh [base-dir]`.
  40 | 2. If `<base-dir>/AKO4ALL` does not exist, the script clones it.
  41 | 3. Do not continue unless `AKO4ALL` is:
  42 |    - on the upstream default branch, usually `main`
  43 |    - fully clean with no tracked or untracked local changes
  44 |    - exactly synced to `upstream/<default-branch>`
  45 | 4. If the script reports local commits, divergence, or a dirty worktree, stop and clean or re-clone the repo before continuing.
  46 | 
  47 | The script creates an `upstream` remote automatically when missing.
  48 | By default it uses the existing `origin` URL, or `AKO4ALL_URL` if you need to override the clone source.
  49 | 
  50 | ## Workflow
  51 | 
  52 | ### 1. Scope the Kernel
  53 | 
  54 | - Identify the exact kernel entry point and runtime call sites in `sglang`.
  55 | - Record the target shapes, dtypes, model families, and whether the kernel is on a hot path.
  56 | - Reuse existing unit tests and benchmark entry points when they already exist.
  57 | 
  58 | If the implementation work is primarily Triton or CUDA authoring, read only the relevant sibling skill from the list above.
  59 | 
  60 | ### 2. Bootstrap the AKO Harness
  61 | 
  62 | Inside the clean `AKO4ALL` repo:
  63 | 
  64 | - read `TASK.md` and `HINTS.md`
  65 | - create a custom harness instead of relying on the stock benchmark tasks
  66 | - mirror the real SGLang kernel into:
  67 |   - `input/reference.py`
  68 |   - `input/<kernel>.py`
  69 |   - `solution/<kernel>.py`
  70 |   - `bench/bench_<kernel>.py`
  71 | - keep a short context note in `context/` when the kernel has model-specific shape assumptions or perf conclusions
  72 | 
  73 | The custom benchmark should:
  74 | 
  75 | - cover representative diffusion shapes
  76 | - check correctness against the reference kernel
  77 | - report aggregate runtime plus per-shape results when useful
  78 | 
  79 | ### 3. Establish the Baseline
  80 | 
  81 | - run the AKO custom microbench before changing the kernel
  82 | - capture one representative `ncu` baseline on the hottest meaningful shape
  83 | - note whether the bottleneck looks like registers, occupancy, instruction count, launch config, or memory latency
  84 | 
  85 | ### 4. Iterate in AKO4ALL
  86 | 
  87 | - change one idea at a time
  88 | - rerun the microbench after every change
  89 | - update `ITERATIONS.md` with hypothesis, result, and next step
  90 | - prefer simple, explainable wins over clever rewrites that do not transfer
  91 | 
  92 | After 3 consecutive no-improvement or regression iterations:
  93 | 
  94 | - rerun `ncu`
  95 | - re-read `ITERATIONS.md`
  96 | - change direction instead of continuing blind sweeps
  97 | 
  98 | ### 5. Port the Best Version Back to SGLang
  99 | 
 100 | - apply the best candidate to the real `sglang` kernel file
 101 | - run import or syntax checks and targeted tests first
 102 | - keep the AKO `solution/` version aligned with the main-tree version you actually want to keep
 103 | 
 104 | ### 6. Validate on Real Models
 105 | 
 106 | - use the benchmark/profile skill for denoise perf dumps and before/after comparison
 107 | - prefer exact local snapshot validation when testing local edits on a GPU box
 108 | - run targeted kernel tests first
 109 | - run model-level denoise benchmarks with perf dumps
 110 | - compare baseline vs optimized runs with `compare_perf.py`
 111 | - if the PR needs proof that generation still works, save one real model output image
 112 | 
 113 | ### 7. Prepare PR Artifacts
 114 | 
 115 | At minimum, keep:
 116 | 
 117 | - one microbench table
 118 | - one denoise-stage table
 119 | - one end-to-end table
 120 | - one `ncu` before/after pair on the most representative kernel shape
 121 | - one generated image when the kernel affects production inference
 122 | 
 123 | See [references/ako-loop.md](references/ako-loop.md) for the checklist and common stop rules.
 124 | 
 125 | ## Operating Rules
 126 | 
 127 | - Treat AKO4ALL repo hygiene as a gate, not a suggestion.
 128 | - Prefer exact local snapshot validation over hand-wavy “remote tree is close enough”.
 129 | - Keep model-level validation honest: if microbench improves but denoise does not, do not keep the AKO-only variant in the main code path.
 130 | - When writing conclusions, explain the win in terms of measurable causes such as lower registers per thread, higher occupancy, fewer executed instructions, or better scheduler eligibility.
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-benchmark-profile/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-benchmark-profile
   3 | description: Use when benchmarking denoise latency or profiling a diffusion bottleneck in SGLang.
   4 | ---
   5 | 
   6 | # SGLang Diffusion Benchmark and Profile
   7 | 
   8 | Use this skill when measuring denoise performance, finding the slow op, checking whether an existing fast path can solve it, or verifying a kernel change in `sglang.multimodal_gen`.
   9 | 
  10 | This skill covers diagnosis and fast-path reuse:
  11 | - To write a new Triton kernel, use [../sglang-diffusion-triton-kernel/SKILL.md](../sglang-diffusion-triton-kernel/SKILL.md)
  12 | - To write a new CUDA JIT kernel, use [../sglang-diffusion-cuda-kernel/SKILL.md](../sglang-diffusion-cuda-kernel/SKILL.md)
  13 | 
  14 | ## Preflight
  15 | 
  16 | Before running any benchmark, profiler, or kernel-validation command:
  17 | - use `scripts/diffusion_skill_env.py` to derive the repo root from `sglang.__file__`
  18 | - verify the repo is writable
  19 | - export `HF_TOKEN` before using gated Hugging Face models such as `black-forest-labs/FLUX.*`
  20 | - export `FLASHINFER_DISABLE_VERSION_CHECK=1`
  21 | - choose idle GPU(s) before starting perf work
  22 | 
  23 | ## Main Reference
  24 | 
  25 | - [benchmark-and-profile.md](benchmark-and-profile.md) — canonical denoise benchmark and profiling workflow; includes `torch.profiler`, `nsys`, and `ncu`
  26 | - [existing-fast-paths.md](existing-fast-paths.md) — map bottlenecks to existing fused kernels and runtime fast paths before writing new code
  27 | - [nsight-profiler.md](nsight-profiler.md) — Nsight Systems / Nsight Compute metric interpretation
  28 | - [scripts/diffusion_skill_env.py](scripts/diffusion_skill_env.py) — preflight helper: repo root discovery via `sglang.__file__`, write-access probe, benchmark/profile output directories, idle GPU selection
  29 | - [scripts/bench_diffusion_rmsnorm.py](scripts/bench_diffusion_rmsnorm.py) — RMSNorm micro-benchmark: JIT CUDA vs PyTorch, correctness check, bandwidth efficiency analysis
  30 | - [scripts/bench_diffusion_denoise.py](scripts/bench_diffusion_denoise.py) — end-to-end denoise benchmark preset runner via `sglang generate`; save perf dumps by label and compare them with `compare_perf.py`
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-cuda-kernel/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-cuda-kernel
   3 | description: Use when writing or tuning a JIT CUDA diffusion kernel in SGLang.
   4 | ---
   5 | 
   6 | # Adding a CUDA Kernel to SGLang Diffusion (JIT Style)
   7 | 
   8 | Use this skill when Triton is not enough and you need vectorized loads, warp reductions, or tighter control over memory layout and occupancy.
   9 | 
  10 | > **Origin**: This skill is adapted from the [HuggingFace kernels cuda-kernels skill](https://github.com/huggingface/kernels/tree/main/skills/cuda-kernels), rewritten to follow SGLang's JIT compilation system and internal abstractions.
  11 | >
  12 | > **Run environment first**: before compiling, benchmarking, or profiling any kernel from this guide, use `../sglang-diffusion-benchmark-profile/scripts/diffusion_skill_env.py` (or the setup block in `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md`) to `cd` to the repo root resolved from `sglang.__file__`, verify write access, export `FLASHINFER_DISABLE_VERSION_CHECK=1`, and pick an idle GPU.
  13 | >
  14 | > **Gated model note**: if you use any FLUX-based `sglang generate` examples from the references below, export `HF_TOKEN` first so the top-level CLI can recognize the gated Hugging Face repo as a diffusion model.
  15 | >
  16 | > **Extended references** (in this directory's `references/` and the sibling benchmark skill):
  17 | > - [references/kernel-templates.md](references/kernel-templates.md) — copy-paste ready templates for element-wise, row-reduction (RMSNorm), fused AdaLN
  18 | > - [references/troubleshooting.md](references/troubleshooting.md) — build errors, perf issues, integration pitfalls
  19 | > - [references/h100-optimization-guide.md](references/h100-optimization-guide.md) — H100 (sm_90) deep dive
  20 | > - [references/a100-optimization-guide.md](references/a100-optimization-guide.md) — A100 (sm_80) deep dive
  21 | > - [references/t4-optimization-guide.md](references/t4-optimization-guide.md) — T4 (sm_75, FP16 only) deep dive
  22 | > - [../sglang-diffusion-benchmark-profile/scripts/bench_diffusion_rmsnorm.py](../sglang-diffusion-benchmark-profile/scripts/bench_diffusion_rmsnorm.py) — RMSNorm micro-benchmark vs PyTorch
  23 | > - [../sglang-diffusion-benchmark-profile/scripts/bench_diffusion_denoise.py](../sglang-diffusion-benchmark-profile/scripts/bench_diffusion_denoise.py) — end-to-end denoise benchmark preset runner; compare perf dumps with `compare_perf.py`
  24 | 
  25 | ## When to Use CUDA vs Triton
  26 | 
  27 | | Scenario | Use |
  28 | |----------|-----|
  29 | | Fused elementwise / norm variants / RoPE | **Triton** (`sglang-diffusion-triton-kernel`) — faster iteration |
  30 | | Bandwidth-bound reduction (RMSNorm, LayerNorm) requiring max vectorization | **CUDA** — full control over `__nv_bfloat162` / `float4` vectorization |
  31 | | Attention pattern or tile-based ops needing shared memory tuning | **CUDA** — warp-level primitives, shared memory layout |
  32 | | Prototype or NPU/CPU fallback needed | **Triton** — portable across backends |
  33 | 
  34 | For most diffusion-model elementwise ops, **start with Triton**. Switch to CUDA when profiling shows Triton can't reach hardware bandwidth limits.
  35 | 
  36 | ## Directory Layout
  37 | 
  38 | ```
  39 | python/sglang/jit_kernel/
  40 | ├── csrc/
  41 | │   ├── diffusion/               # JIT CUDA source files for diffusion kernels (this skill)
  42 | │   │   ├── timestep_embedding.cuh   # existing example
  43 | │   │   ├── rmsnorm.cuh              # NEW: add here
  44 | │   │   └── adaln.cuh                # NEW: add here
  45 | │   └── elementwise/             # shared JIT CUDA csrc (non-diffusion)
  46 | ├── diffusion/
  47 | │   ├── triton/                  # Triton kernels (scale_shift, norm, rope, ...)
  48 | │   ├── cutedsl/                 # CuTe DSL kernels
  49 | │   └── rmsnorm.py               # NEW: CUDA JIT Python wrapper (add here)
  50 | ├── timestep_embedding.py        # existing CUDA diffusion kernel Python wrapper (legacy)
  51 | ```
  52 | 
  53 | New diffusion CUDA kernel source files go into `python/sglang/jit_kernel/csrc/diffusion/<op_name>.cuh`.
  54 | The Python wrapper goes at `python/sglang/jit_kernel/diffusion/<op_name>.py`
  55 | (inside `diffusion/`, alongside the `triton/` and `cutedsl/` subdirectories).
  56 | 
  57 | ---
  58 | 
  59 | ## SGLang Kernel Abstractions (Required)
  60 | 
  61 | Always use these — do **not** use raw CUDA primitives directly.
  62 | 
  63 | ```cpp
  64 | #include <sgl_kernel/tensor.h>    // TensorMatcher, SymbolicSize, SymbolicDevice
  65 | #include <sgl_kernel/type.cuh>    // fp16_t, bf16_t, fp32_t, dtype_trait, packed_t
  66 | #include <sgl_kernel/utils.h>     // RuntimeCheck, div_ceil
  67 | #include <sgl_kernel/utils.cuh>   // LaunchKernel, SGL_DEVICE, type aliases
  68 | #include <sgl_kernel/vec.cuh>     // AlignedVector<T, N> — 128-bit vector loads
  69 | #include <sgl_kernel/warp.cuh>    // warp::reduce_sum, warp::reduce_max
  70 | #include <sgl_kernel/math.cuh>    // device::math::rsqrt, sqrt, ...
  71 | #include <sgl_kernel/tile.cuh>    // tile::Memory (strided access pattern)
  72 | ```
  73 | 
  74 | Key types: `fp16_t` = `__half`, `bf16_t` = `__nv_bfloat16`, `fp32_t` = `float`.
  75 | Packed variants: `fp16x2_t`, `bf16x2_t`. Use `packed_t<T>` for the 2-element alias.
  76 | 
  77 | ---
  78 | 
  79 | ## Step 1: Write the CUDA Kernel
  80 | 
  81 | Create `python/sglang/jit_kernel/csrc/diffusion/rmsnorm.cuh` (RMSNorm as example).
  82 | 
  83 | ### 1a. Vectorized RMSNorm Kernel
  84 | 
  85 | ```cpp
  86 | #include <sgl_kernel/tensor.h>
  87 | #include <sgl_kernel/type.cuh>
  88 | #include <sgl_kernel/utils.h>
  89 | #include <sgl_kernel/utils.cuh>
  90 | #include <sgl_kernel/vec.cuh>
  91 | #include <sgl_kernel/warp.cuh>
  92 | 
  93 | #include <dlpack/dlpack.h>
  94 | #include <tvm/ffi/container/tensor.h>
  95 | 
  96 | namespace {
  97 | 
  98 | // ---------------------------------------------------------------
  99 | // RMSNorm kernel: y = x / rms(x) * weight
 100 | // T      = fp16_t | bf16_t | fp32_t
 101 | // kVecN  = vectorized elements per load (8 for fp16/bf16, 4 for fp32)
 102 | // ---------------------------------------------------------------
 103 | template <typename T, int kVecN>
 104 | __global__ void rmsnorm_kernel(
 105 |     T* __restrict__ dst,
 106 |     const T* __restrict__ src,
 107 |     const T* __restrict__ weight,        // may be nullptr if no affine weight
 108 |     uint32_t hidden_size,
 109 |     uint32_t n_vecs,                     // hidden_size / kVecN
 110 |     float eps)
 111 | {
 112 |     using vec_t = device::AlignedVector<T, kVecN>;
 113 | 
 114 |     const uint32_t row = blockIdx.x;
 115 |     const T* row_src = src + row * hidden_size;
 116 |     T*       row_dst = dst + row * hidden_size;
 117 | 
 118 |     // --- Pass 1: accumulate sum of squares (vectorized) ---
 119 |     float sum_sq = 0.f;
 120 |     for (uint32_t vi = threadIdx.x; vi < n_vecs; vi += blockDim.x) {
 121 |         vec_t v;
 122 |         v.load(row_src, vi);
 123 |         #pragma unroll
 124 |         for (int i = 0; i < kVecN; ++i) {
 125 |             float val = static_cast<float>(v[i]);
 126 |             sum_sq += val * val;
 127 |         }
 128 |     }
 129 | 
 130 |     // --- Warp reduction ---
 131 |     sum_sq = device::warp::reduce_sum<float>(sum_sq);
 132 | 
 133 |     // --- Block reduction via shared memory ---
 134 |     __shared__ float smem[32];
 135 |     if (threadIdx.x % 32 == 0) {
 136 |         smem[threadIdx.x / 32] = sum_sq;
 137 |     }
 138 |     __syncthreads();
 139 |     if (threadIdx.x < 32) {
 140 |         sum_sq = (threadIdx.x < blockDim.x / 32) ? smem[threadIdx.x] : 0.f;
 141 |         sum_sq = device::warp::reduce_sum<float>(sum_sq);
 142 |     }
 143 |     __syncthreads();
 144 | 
 145 |     const float rms_inv = device::math::rsqrt<float>(sum_sq / static_cast<float>(hidden_size) + eps);
 146 | 
 147 |     // --- Pass 2: normalize + apply weight (vectorized) ---
 148 |     for (uint32_t vi = threadIdx.x; vi < n_vecs; vi += blockDim.x) {
 149 |         vec_t v_in, v_w, v_out;
 150 |         v_in.load(row_src, vi);
 151 |         if (weight != nullptr) {
 152 |             v_w.load(weight, vi);
 153 |         }
 154 |         #pragma unroll
 155 |         for (int i = 0; i < kVecN; ++i) {
 156 |             float val = static_cast<float>(v_in[i]) * rms_inv;
 157 |             if (weight != nullptr) {
 158 |                 val *= static_cast<float>(v_w[i]);
 159 |             }
 160 |             v_out[i] = static_cast<T>(val);
 161 |         }
 162 |         v_out.store(row_dst, vi);
 163 |     }
 164 | }
 165 | 
 166 | // ---------------------------------------------------------------
 167 | // Launcher
 168 | // ---------------------------------------------------------------
 169 | template <typename T>
 170 | void rmsnorm(
 171 |     tvm::ffi::TensorView dst,
 172 |     tvm::ffi::TensorView src,
 173 |     tvm::ffi::TensorView weight,          // pass empty / nullptr for no-weight case
 174 |     float eps)
 175 | {
 176 |     using namespace host;
 177 | 
 178 |     // Validate
 179 |     SymbolicSize B{"batch_tokens"}, H{"hidden_size"};
 180 |     SymbolicDevice device;
 181 |     device.set_options<kDLCUDA>();
 182 | 
 183 |     TensorMatcher({B, H})
 184 |         .with_dtype<T>()
 185 |         .with_device(device)
 186 |         .verify(dst)
 187 |         .verify(src);
 188 | 
 189 |     const uint32_t num_rows   = static_cast<uint32_t>(B.unwrap());
 190 |     const uint32_t hidden     = static_cast<uint32_t>(H.unwrap());
 191 |     const DLDevice dev        = device.unwrap();
 192 | 
 193 |     RuntimeCheck(hidden % (16 / sizeof(T)) == 0,
 194 |         "rmsnorm: hidden_size must be divisible by vector width, got ", hidden);
 195 | 
 196 |     constexpr int kVecN    = 16 / sizeof(T);   // 128-bit vector: 8×fp16/bf16, 4×fp32
 197 |     const uint32_t n_vecs  = hidden / kVecN;
 198 | 
 199 |     // Thread count: enough warps to cover n_vecs, max 512 threads
 200 |     uint32_t threads = std::min(n_vecs, 512u);
 201 |     threads = (threads + 31) / 32 * 32;   // round up to warp boundary
 202 | 
 203 |     const T* w_ptr = (weight.data_ptr() != nullptr)
 204 |         ? static_cast<const T*>(weight.data_ptr()) : nullptr;
 205 | 
 206 |     LaunchKernel(num_rows, threads, dev)(
 207 |         rmsnorm_kernel<T, kVecN>,
 208 |         static_cast<T*>(dst.data_ptr()),
 209 |         static_cast<const T*>(src.data_ptr()),
 210 |         w_ptr,
 211 |         hidden,
 212 |         n_vecs,
 213 |         eps);
 214 | }
 215 | 
 216 | }  // namespace
 217 | ```
 218 | 
 219 | ---
 220 | 
 221 | ## Step 2: Python Wrapper
 222 | 
 223 | Create `python/sglang/jit_kernel/diffusion/rmsnorm.py`:
 224 | 
 225 | ```python
 226 | from __future__ import annotations
 227 | from typing import TYPE_CHECKING
 228 | 
 229 | import torch
 230 | 
 231 | from sglang.jit_kernel.utils import (
 232 |     cache_once,
 233 |     is_arch_support_pdl,
 234 |     load_jit,
 235 |     make_cpp_args,
 236 | )
 237 | 
 238 | if TYPE_CHECKING:
 239 |     from tvm_ffi.module import Module
 240 | 
 241 | 
 242 | @cache_once
 243 | def _jit_rmsnorm_module(hidden_size: int, dtype: torch.dtype) -> Module:
 244 |     args = make_cpp_args(hidden_size, is_arch_support_pdl(), dtype)
 245 |     return load_jit(
 246 |         "diffusion_rmsnorm",
 247 |         *args,
 248 |         cuda_files=["diffusion/rmsnorm.cuh"],  # relative to csrc/
 249 |         cuda_wrappers=[("rmsnorm", f"RMSNormKernel<{args}>::run")],
 250 |     )
 251 | 
 252 | 
 253 | def diffusion_rmsnorm(
 254 |     src: torch.Tensor,
 255 |     weight: torch.Tensor | None = None,
 256 |     eps: float = 1e-6,
 257 |     out: torch.Tensor | None = None,
 258 | ) -> torch.Tensor:
 259 |     """
 260 |     RMSNorm for diffusion DiT layers.
 261 | 
 262 |     y = x / rms(x) * weight   (weight=None → no affine scaling)
 263 | 
 264 |     Supported fast path: float16 / bfloat16.
 265 |     For unsupported combinations (for example some float32 configs),
 266 |     fall back to torch.nn.functional.rms_norm.
 267 |     """
 268 |     assert src.is_cuda, "src must be a CUDA tensor"
 269 |     assert src.dtype in (torch.float16, torch.bfloat16, torch.float32)
 270 |     hidden_size = src.shape[-1]
 271 | 
 272 |     if out is None:
 273 |         out = torch.empty_like(src)
 274 | 
 275 |     w = weight if weight is not None else torch.ones(hidden_size, dtype=src.dtype, device=src.device)
 276 | 
 277 |     module = _jit_rmsnorm_module(hidden_size, src.dtype)
 278 |     module.rmsnorm(src.reshape(-1, hidden_size), w, out.reshape(-1, hidden_size), eps)
 279 |     return out
 280 | ```
 281 | 
 282 | **Key rules for the wrapper:**
 283 | - Use `cache_once` — never `functools.lru_cache` (breaks `torch.compile`)
 284 | - Include every compile-time specialization parameter in the cache key (`hidden_size`, PDL support, dtype here)
 285 | - `cuda_files` are relative to `python/sglang/jit_kernel/csrc/`
 286 | - `cuda_wrappers`: `(python_name, cpp_template_instantiation)`
 287 | 
 288 | ---
 289 | 
 290 | ## Step 3: Integrate into Runtime (Optional, After Standalone Validation)
 291 | 
 292 | The kernel replaces a slow operator inside the DiT forward pass. Find the correct module in:
 293 | 
 294 | ```
 295 | python/sglang/multimodal_gen/runtime/pipelines_core/stages/denoising.py
 296 | python/sglang/multimodal_gen/runtime/models/dits/<model>.py
 297 | ```
 298 | 
 299 | There is no built-in `SGLANG_DIFFUSION_CUSTOM_CUDA_KERNELS` hook in the runtime. After the standalone test/benchmark passes, wire the new kernel into the actual execution path explicitly. A minimal pattern is to monkey-patch the target RMSNorm modules before `torch.compile` or any CPU offload setup:
 300 | 
 301 | ```python
 302 | from sglang.jit_kernel.diffusion.rmsnorm import diffusion_rmsnorm
 303 | 
 304 | def _patch_rmsnorm(model: torch.nn.Module) -> None:
 305 |     for name, module in model.named_modules():
 306 |         cls_name = type(module).__name__
 307 |         if cls_name in ("RMSNorm", "LlamaRMSNorm") or "RMSNorm" in cls_name:
 308 |             eps = getattr(module, "eps", getattr(module, "variance_epsilon", 1e-6))
 309 |             has_weight = hasattr(module, "weight") and module.weight is not None
 310 | 
 311 |             if has_weight:
 312 |                 def _make_fwd(mod, epsilon):
 313 |                     def forward(x):
 314 |                         return diffusion_rmsnorm(x, weight=mod.weight, eps=epsilon)
 315 |                     return forward
 316 |                 module.forward = _make_fwd(module, eps)
 317 |             else:
 318 |                 def _make_fwd_noweight(epsilon):
 319 |                     def forward(x):
 320 |                         return diffusion_rmsnorm(x, weight=None, eps=epsilon)
 321 |                     return forward
 322 |                 module.forward = _make_fwd_noweight(eps)
 323 | ```
 324 | 
 325 | **Critical:** inject kernels **before** `torch.compile` and before any CPU offload is enabled.
 326 | 
 327 | ---
 328 | 
 329 | ## Step 4: Key Kernel Patterns Reference
 330 | 
 331 | ### Diffusion-Specific Operators
 332 | 
 333 | | Operator | Kernel Pattern | Notes |
 334 | |----------|---------------|-------|
 335 | | **RMSNorm** | 2-pass row reduction + vectorized normalize | Weight may be `None` (`elementwise_affine=False`) |
 336 | | **AdaLN modulation** | `y = norm(x) * (1 + scale) + shift` | Fuse norm + scale + shift in one pass |
 337 | | **RoPE 3D** | Read `(t, h, w)` cos/sin tables, apply to `(q, k)` | Layout: `[batch, t*h*w, heads, head_dim]` |
 338 | | **GEGLU** | Split last dim → `gate * silu(linear)` | Input `[B, L, 2*H]` → output `[B, L, H]` |
 339 | | **SiLU gate** | `out = a * sigmoid(a)` fused | Avoid separate elementwise ops |
 340 | 
 341 | ### Vectorized Memory Access
 342 | 
 343 | ```cpp
 344 | // BF16: 8 elements × 2 bytes = 16 bytes per vector load (AlignedVector<bf16_t, 8>)
 345 | // FP16: 8 elements × 2 bytes = 16 bytes (AlignedVector<fp16_t, 8>)
 346 | // FP32: 4 elements × 4 bytes = 16 bytes (AlignedVector<fp32_t, 4>)
 347 | constexpr int kVecN = 16 / sizeof(T);
 348 | using vec_t = device::AlignedVector<T, kVecN>;
 349 | ```
 350 | 
 351 | ### Warp / Block Reductions
 352 | 
 353 | ```cpp
 354 | // Warp reduction (within 32 threads)
 355 | float result = device::warp::reduce_sum<float>(partial);
 356 | 
 357 | // Block reduction via shared memory (see rmsnorm example above)
 358 | __shared__ float smem[32];
 359 | // ... write warp-leaders into smem, sync, reduce again
 360 | ```
 361 | 
 362 | ### Thread Configuration
 363 | 
 364 | ```cpp
 365 | // Element-wise (RoPE, GEGLU, SiLU): simple 1D grid
 366 | constexpr uint32_t kBlock = 256;
 367 | uint32_t grid = host::div_ceil(total_elements, kBlock);
 368 | LaunchKernel(grid, kBlock, dev)(kernel, ...);
 369 | 
 370 | // Row reduction (RMSNorm, LayerNorm): one block per row
 371 | uint32_t threads = std::min(hidden_size / kVecN, 512u);
 372 | threads = (threads + 31) / 32 * 32;
 373 | LaunchKernel(num_rows, threads, dev)(kernel, ...);
 374 | ```
 375 | 
 376 | ---
 377 | 
 378 | ## Step 5: GPU Architecture Targets
 379 | 
 380 | | GPU | Compute Cap | Memory BW | BF16 | Key Note |
 381 | |-----|------------|-----------|------|----------|
 382 | | H100 | sm_90 | 3.35 TB/s | Yes | Primary target; 132 SMs, 192 KB shared mem/SM |
 383 | | A100 | sm_80 | 2.0 TB/s  | Yes | 108 SMs, 164 KB shared mem/SM |
 384 | | T4   | sm_75 | 320 GB/s  | **No** | FP16 only; no `__nv_bfloat16` |
 385 | 
 386 | If kernel requires SM90+ features (e.g., TMA, wgmma), raise a clear error:
 387 | 
 388 | ```python
 389 | if torch.cuda.get_device_capability()[0] < 9:
 390 |     raise RuntimeError("This kernel requires SM90 (H100/Hopper) or later")
 391 | ```
 392 | 
 393 | **Grid sizing for H100** (132 SMs): aim for grid multiples of 132 for good occupancy.
 394 | 
 395 | ---
 396 | 
 397 | ## Step 6: Tests
 398 | 
 399 | For this tutorial kernel, the repo now includes a verified regression test at `python/sglang/jit_kernel/tests/test_diffusion_rmsnorm.py`. Model new kernel tests after it:
 400 | 
 401 | ```python
 402 | import pytest
 403 | import torch
 404 | from sglang.jit_kernel.diffusion.rmsnorm import diffusion_rmsnorm
 405 | 
 406 | 
 407 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 408 | @pytest.mark.parametrize("shape", [(1, 2048), (4, 3072), (16, 4096)])
 409 | @pytest.mark.parametrize("has_weight", [True, False])
 410 | def test_rmsnorm_correctness(dtype, shape, has_weight):
 411 |     batch, hidden = shape
 412 |     src = torch.randn(batch, hidden, dtype=dtype, device="cuda")
 413 |     weight = torch.randn(hidden, dtype=dtype, device="cuda") if has_weight else None
 414 | 
 415 |     out_jit = diffusion_rmsnorm(src, weight=weight, eps=1e-6)
 416 | 
 417 |     # Reference: torch.nn.functional
 418 |     ref = torch.nn.functional.rms_norm(
 419 |         src.float(), (hidden,), weight.float() if weight is not None else None, eps=1e-6
 420 |     ).to(dtype)
 421 | 
 422 |     tol = {"rtol": 1e-2, "atol": 1e-2} if dtype != torch.float32 else {"rtol": 1e-5, "atol": 1e-6}
 423 |     torch.testing.assert_close(out_jit, ref, **tol)
 424 | 
 425 | 
 426 | if __name__ == "__main__":
 427 |     import sys
 428 |     sys.exit(pytest.main([__file__, "-v", "-s"]))
 429 | ```
 430 | 
 431 | ---
 432 | 
 433 | ## Step 7: Benchmark
 434 | 
 435 | For the RMSNorm example in this skill, use the checked-in micro-benchmark script `scripts/bench_diffusion_rmsnorm.py`. For new kernels, follow the same structure or model a `triton.testing` benchmark after `python/sglang/jit_kernel/benchmark/bench_rmsnorm.py`.
 436 | 
 437 | ---
 438 | 
 439 | ## Step 8: Profile with Nsight Compute (required)
 440 | 
 441 | After correctness + benchmarking, you must collect **Nsight Compute (ncu)** data to validate:
 442 | 
 443 | - Whether the kernel reaches reasonable bandwidth/throughput (avoid false positives where it is “faster” but under-utilizes hardware)
 444 | - Whether there are clear occupancy / register / shared memory limiters
 445 | 
 446 | Use the canonical docs in this directory (do not duplicate CLI details across multiple skills):
 447 | 
 448 | - `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md` → Step 3.5 (ncu workflow, including CUDA graph profiling)
 449 | - `../sglang-diffusion-benchmark-profile/nsight-profiler.md` (metrics interpretation: bandwidth / occupancy / roofline / stall reasons)
 450 | 
 451 | ---
 452 | 
 453 | ## Common Pitfalls
 454 | 
 455 | | Issue | Fix |
 456 | |-------|-----|
 457 | | `RMSNorm weight is None` | Use `type(module).__name__` check; pass `None` weight explicitly |
 458 | | `isinstance(m, torch.nn.RMSNorm)` misses diffusers variants | Use `"RMSNorm" in type(m).__name__` |
 459 | | Kernel patched after `torch.compile` | Inject **before** any compile call |
 460 | | Kernel patched after `enable_model_cpu_offload()` | Inject **before** CPU offload |
 461 | | `hidden_size` not divisible by `kVecN` | Add `RuntimeCheck(hidden % kVecN == 0, ...)` in launcher |
 462 | | `torch.compile` fails with custom CUDA kernel | Register as `@torch.library.custom_op` or use Triton instead |
 463 | | T4 GPU with BF16 kernel | Gate on compute capability; T4 is `sm_75`, no native BF16 |
 464 | 
 465 | ---
 466 | 
 467 | ## Summary of Files
 468 | 
 469 | ```
 470 | python/sglang/jit_kernel/csrc/diffusion/
 471 | └── rmsnorm.cuh                                  # NEW: JIT CUDA kernel source
 472 | 
 473 | python/sglang/jit_kernel/diffusion/
 474 | └── rmsnorm.py                                   # NEW: Python wrapper + load_jit
 475 | 
 476 | python/sglang/jit_kernel/tests/
 477 | └── test_diffusion_rmsnorm.py                    # NEW: correctness tests
 478 | 
 479 | python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-benchmark-profile/scripts/
 480 | ├── bench_diffusion_rmsnorm.py                   # Validated micro-benchmark used by this skill
 481 | └── bench_diffusion_denoise.py                   # Preset runner for end-to-end perf dumps
 482 | ```
 483 | 
 484 | ---
 485 | 
 486 | ## References
 487 | 
 488 | ### This Skill's Extended Docs (references/ and scripts/)
 489 | 
 490 | | File | Contents |
 491 | |------|----------|
 492 | | [references/kernel-templates.md](references/kernel-templates.md) | Copy-paste templates: element-wise, RMSNorm, AdaLN, Python wrapper, test, benchmark |
 493 | | [references/troubleshooting.md](references/troubleshooting.md) | Build errors, perf issues, torch.compile compatibility, debugging checklist |
 494 | | [references/h100-optimization-guide.md](references/h100-optimization-guide.md) | H100 (sm_90): memory hierarchy, warp reductions, occupancy, vectorization benchmarks |
 495 | | [references/a100-optimization-guide.md](references/a100-optimization-guide.md) | A100 (sm_80): cp.async, TF32, 2:4 sparsity, H100→A100 migration checklist |
 496 | | [references/t4-optimization-guide.md](references/t4-optimization-guide.md) | T4 (sm_75): FP16 only, low bandwidth, tile size limits, memory constraints |
 497 | | [scripts/bench_diffusion_rmsnorm.py](scripts/bench_diffusion_rmsnorm.py) | Micro-benchmark: JIT CUDA RMSNorm vs PyTorch, correctness check, bandwidth analysis |
 498 | | [scripts/bench_diffusion_denoise.py](scripts/bench_diffusion_denoise.py) | End-to-end preset runner. Save perf dumps per label, then compare with `compare_perf.py` |
 499 | 
 500 | ### SGLang Internals
 501 | 
 502 | - **JIT system**: `add-jit-kernel` skill (`sglang/.claude/skills/add-jit-kernel/SKILL.md`)
 503 | - **JIT utils**: `python/sglang/jit_kernel/utils.py` — `cache_once`, `load_jit`, `make_cpp_args`
 504 | - **Abstractions**: `python/sglang/jit_kernel/include/sgl_kernel/` — `tensor.h`, `utils.cuh`, `vec.cuh`, `warp.cuh`, `math.cuh`, `tile.cuh`
 505 | - **Real csrc examples**: `python/sglang/jit_kernel/csrc/elementwise/rmsnorm.cuh`, `python/sglang/jit_kernel/csrc/elementwise/qknorm.cuh`
 506 | 
 507 | ### Other Diffusion Kernel Skills (this directory)
 508 | 
 509 | - **Triton alternative**: `../sglang-diffusion-triton-kernel/SKILL.md` — prefer Triton unless bandwidth analysis shows CUDA needed
 510 | - **Existing fused kernels**: `../sglang-diffusion-benchmark-profile/existing-fast-paths.md` — check here first before writing new kernels
 511 | - **Profiling**: `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md` — workflow to identify bottleneck before implementing
 512 | - **Nsight Compute deep dive**: `../sglang-diffusion-benchmark-profile/nsight-profiler.md` — full guide: occupancy analysis, roofline model, warp efficiency, kernel comparison
 513 | 
 514 | ### External
 515 | 
 516 | - [HuggingFace kernels cuda-kernels skill](https://github.com/huggingface/kernels/tree/main/skills/cuda-kernels) — original source adapted for this skill
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-performance/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-performance
   3 | description: Use when choosing the fastest SGLang Diffusion flags for a model, GPU, and VRAM budget.
   4 | ---
   5 | 
   6 | # SGLang Diffusion Performance Tuning
   7 | 
   8 | Use this skill when the user wants the fastest command line, lower VRAM, or the right performance flags for a specific model and GPU setup.
   9 | 
  10 | Before running any `sglang generate` command below inside the diffusion container:
  11 | - use `python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-benchmark-profile/scripts/diffusion_skill_env.py` to derive the repo root, verify write access, and choose idle GPU(s)
  12 | - export `HF_TOKEN` first when the selected model lives in a gated Hugging Face repo such as `black-forest-labs/FLUX.*`
  13 | - export `FLASHINFER_DISABLE_VERSION_CHECK=1`
  14 | - `cd` to the repo root resolved from `sglang.__file__`
  15 | 
  16 | Reference: [SGLang-Diffusion Advanced Optimizations Blog](https://lmsys.org/blog/2026-02-16-sglang-diffusion-advanced-optimizations/)
  17 | 
  18 | ---
  19 | 
  20 | ## Section 1: Lossless Optimizations
  21 | 
  22 | These options are intended to preserve output quality. In practice, some paths (most notably `torch.compile`) can still introduce small floating-point drift, so validate on your target model when numerical parity matters.
  23 | 
  24 | | Option | CLI Flag / Env Var | What It Does | Speedup | Limitations / Notes |
  25 | |---|---|---|---|---|
  26 | | **torch.compile** | `--enable-torch-compile` | Applies `torch.compile` to the DiT forward pass, fusing ops and reducing kernel launch overhead. | ~1.2–1.5x on denoising | First request is slow (compilation). May cause minor precision drifts due to [PyTorch issue #145213](https://github.com/pytorch/pytorch/issues/145213). Pair with `--warmup` for best results. |
  27 | | **Warmup** | `--warmup` | Runs dummy forward passes to warm up CUDA caches, JIT, and `torch.compile`. Eliminates cold-start penalty. | Removes first-request latency spike | Adds startup time. Without `--warmup-resolutions`, warmup happens on first request. |
  28 | | **Warmup Resolutions** | `--warmup-resolutions 256x256 720x720` | Pre-compiles and warms up specific resolutions at server startup (instead of lazily on first request). | Faster first request per resolution | Each resolution adds to startup time. Serving mode only; useful when you know your target resolutions in advance. |
  29 | | **Multi-GPU (SP)** | `--num-gpus N --ulysses-degree N` | Sequence parallelism across GPUs. Shards sequence tokens (not frames) to minimize padding. | Near-linear scaling with N GPUs | Requires NCCL; inter-GPU bandwidth matters. `ulysses_degree * ring_degree = sp_degree`. |
  30 | | **CFG Parallel** | `--enable-cfg-parallel` | Runs conditional and unconditional CFG branches in parallel across GPUs. For CFG models on multi-GPU, benchmark this against pure Ulysses on your topology instead of assuming one always wins. | Often faster than pure SP for CFG models | Requires `num_gpus >= 2`. Halves the Ulysses group size (e.g. 8 GPU → two 4-GPU groups). Only for models that use CFG. |
  31 | | **Layerwise Offload** | `--dit-layerwise-offload` | Async layer-by-layer H2D prefetch with compute overlap. Only ~2 DiT layers reside on GPU at a time, dramatically reducing VRAM. For some video models the copy stream can be almost fully hidden behind compute ([PR #15511](https://github.com/sgl-project/sglang/pull/15511)). | Saves VRAM (40 GB → ~11 GB for Wan A14B); can be near-zero speed cost on the right workload | Enabled by default for Wan/MOVA video models. Incompatible with Cache-DiT. For **image models** or highly parallelized setups (many GPUs, small per-GPU compute), the copy stream may not be fully hidden and can cause slowdown. |
  32 | | **Offload Prefetch Size** | `--dit-offload-prefetch-size F` | Fine-grained control over layerwise offload: how many layers to prefetch ahead. `0.0` = 1 layer (min VRAM), `0.1` = 10% of layers, `≥1` = absolute layer count. | Tune for cases where default offload has copy stream interference (e.g. image models). 0.05–0.1 is a good starting point. | Values ≥ 0.5 approach no-offload VRAM with worse performance. See [PR #17693](https://github.com/sgl-project/sglang/pull/17693) for benchmarks on image models. |
  33 | | **FSDP Inference** | `--use-fsdp-inference` | Uses PyTorch FSDP to shard model weights across GPUs with prefetch. Low latency, low VRAM. | Reduces per-GPU VRAM | Mutually exclusive with `--dit-layerwise-offload`. More overhead than SP on high-bandwidth interconnects. |
  34 | | **CPU Offload (components)** | `--text-encoder-cpu-offload`, `--image-encoder-cpu-offload`, `--vae-cpu-offload`, `--dit-cpu-offload` | Offloads specific pipeline components to CPU when not in use. | Reduces peak VRAM | Adds H2D transfer latency when the component is needed. Auto-enabled for low-VRAM GPUs (<30 GB). **Tip:** after the first request completes, the console prints a peak VRAM analysis with suggestions on which offload flags can be safely disabled — look for the `"Components that could stay resident"` log line. |
  35 | | **Pin CPU Memory** | `--pin-cpu-memory` | Uses pinned (page-locked) memory for CPU offload transfers. | Faster H2D transfers | Slightly higher host memory usage. Enabled by default; disable only as workaround for CUDA errors. |
  36 | | **Attention Backend (lossless)** | `--attention-backend fa` | Selects a lossless attention kernel for SGLang-native pipelines: `fa` (FlashAttention 2/3/4 alias) or `torch_sdpa`. | FA is usually faster than SDPA on long sequences | FA requires compatible GPU (Ampere+). For `--backend diffusers`, valid backend names differ; use the names documented in `docs/diffusion/performance/attention_backends.md`. |
  37 | | **Parallel Folding** | *(automatic when SP > 1)* | Reuses the SP process group as TP for the T5 text encoder, so text encoding is parallelized "for free". | Faster text encoding on multi-GPU | Automatic; no user action needed. Only applies to T5-based pipelines. |
  38 | 
  39 | ---
  40 | 
  41 | ## Section 2: Lossy Optimizations
  42 | 
  43 | These options **trade output quality** for speed or VRAM savings. Results will differ from the baseline.
  44 | 
  45 | | Option | CLI Flag / Env Var | What It Does | Speedup | Quality Impact / Limitations |
  46 | |---|---|---|---|---|
  47 | | **Approximate Attention** | `--attention-backend sage_attn` / `sage_attn_3` / `sliding_tile_attn` / `video_sparse_attn` / `sparse_video_gen_2_attn` / `vmoba_attn` / `sla_attn` / `sage_sla_attn` | Replaces exact attention with approximate or sparse variants. `sage_attn`: INT8/FP8 quantized Q·K; `sliding_tile_attn`: spatial-temporal tile skipping; others: model-specific sparse patterns. | ~1.5–2x on attention (varies by backend) | Quality degradation varies by backend and model. `sage_attn` is the most general; sparse backends (`sliding_tile_attn`, `video_sparse_attn`, etc.) are video-model-specific and may require config files (e.g. `--mask-strategy-file-path` for STA). Requires corresponding packages installed. |
  48 | | **Cache-DiT** | `SGLANG_CACHE_DIT_ENABLED=true` + `--cache-dit-config <path>` | Caches intermediate residuals across denoising steps and skips redundant computations via a Selective Computation Mask (SCM). | ~1.5–2x on supported models | Quality depends on SCM config. Incompatible with `--dit-layerwise-offload`. Requires correct per-model config YAML. |
  49 | | **Quantized Models (Nunchaku / SVDQuant)** | `--enable-svdquant --transformer-weights-path <path>` + optional `--quantization-precision int4\|nvfp4`, `--quantization-rank 32` | W4A4-style quantization via [Nunchaku](https://nunchaku.tech). Reduces DiT weight memory by ~4x. Precision/rank can be auto-inferred from weight filename or set explicitly. | ~1.5–2x compute speedup | Lossy quantization; quality depends on rank and precision. Requires pre-quantized weights. Ampere (SM8x) or SM12x only (no Hopper SM90). Higher rank = better quality but more memory. |
  50 | | **Pre-quantized Weights** | `--transformer-weights-path <path>` | Load any pre-quantized transformer weights (FP8, INT8, etc.) from a single `.safetensors` file, a directory, or a HuggingFace repo ID. | ~1.3–1.5x compute (dtype dependent) | Requires pre-converted weights (e.g. via `tools/convert_hf_to_fp8.py` for FP8). Quality slightly worse than BF16; varies by quantization format. |
  51 | | **Component Precision Override** | `--dit-precision fp16`, `--vae-precision fp16\|bf16` | On-the-fly dtype conversion for individual components. E.g. convert a BF16 model to FP16 at load time, or run VAE in BF16 instead of FP32. | Reduces memory; FP16 can be faster on some GPUs | May affect numerical stability. VAE is FP32 by default for accuracy; lowering it is lossy. DiT defaults to BF16. |
  52 | | **Fewer Inference Steps** | `--num-inference-steps N` (sampling param) | Reduces the number of denoising steps. Fewer steps = faster. | Linear speedup | Quality degrades with too few steps. Model-dependent optimal range. |
  53 | 
  54 | ---
  55 | 
  56 | ## Quick Recipes
  57 | 
  58 | ### Maximum speed, video model, multi-GPU, lossless (Wan A14B, 8 GPUs)
  59 | 
  60 | ```bash
  61 | sglang generate --model-path Wan-AI/Wan2.2-T2V-A14B-Diffusers \
  62 |   --num-gpus 8 --enable-cfg-parallel --ulysses-degree 4 \
  63 |   --enable-torch-compile --warmup \
  64 |   --text-encoder-cpu-offload true \
  65 |   --prompt "..." --save-output
  66 | ```
  67 | 
  68 | Note: `--dit-layerwise-offload` is enabled by default for Wan/MOVA video models and is often a good default, but still benchmark it on your exact workload if latency matters.
  69 | 
  70 | ### Maximum speed, image model, single GPU, lossless
  71 | 
  72 | ```bash
  73 | sglang generate --model-path <IMAGE_MODEL> \
  74 |   --enable-torch-compile --warmup \
  75 |   --dit-layerwise-offload false \
  76 |   --prompt "..." --save-output
  77 | ```
  78 | 
  79 | Note: for image models, per-layer compute is smaller, so layerwise offload may not fully hide H2D transfer. Disable it if VRAM allows.
  80 | 
  81 | ### Low VRAM, decent speed (single GPU)
  82 | 
  83 | ```bash
  84 | sglang generate --model-path <MODEL> \
  85 |   --enable-torch-compile --warmup \
  86 |   --dit-layerwise-offload --dit-offload-prefetch-size 0.1 \
  87 |   --text-encoder-cpu-offload true --vae-cpu-offload true \
  88 |   --prompt "..." --save-output
  89 | ```
  90 | 
  91 | ### Maximum speed, lossy (SageAttention + Cache-DiT)
  92 | 
  93 | ```bash
  94 | SGLANG_CACHE_DIT_ENABLED=true sglang generate --model-path <MODEL> \
  95 |   --attention-backend sage_attn \
  96 |   --cache-dit-config <config.yaml> \
  97 |   --enable-torch-compile --warmup \
  98 |   --dit-layerwise-offload false \
  99 |   --prompt "..." --save-output
 100 | ```
 101 | 
 102 | ---
 103 | 
 104 | ## Tips
 105 | 
 106 | - **Benchmarking**: always use `--warmup` and look for the line ending with `(with warmup excluded)` for accurate timing.
 107 | - **Perf dump**: use `--perf-dump-path result.json` to save structured metrics, then compare with `python python/sglang/multimodal_gen/benchmarks/compare_perf.py baseline.json result.json`.
 108 | - **Offload tuning**: after the first request, the runtime logs peak GPU memory and which components could stay resident. Use this to decide which `--*-cpu-offload` flags to disable.
 109 | - **Backend selection**: `--backend sglang` (default, auto-detected) enables all native optimizations (fused kernels, SP, etc.). `--backend diffusers` falls back to vanilla Diffusers pipelines but supports `--cache-dit-config` and diffusers attention backends.
```


---
## python/sglang/multimodal_gen/.claude/skills/sglang-diffusion-triton-kernel/SKILL.md

```
   1 | ---
   2 | name: sglang-diffusion-triton-kernel
   3 | description: Use when writing or tuning a Triton diffusion kernel in SGLang.
   4 | ---
   5 | 
   6 | # Adding a Triton Kernel to SGLang Diffusion
   7 | 
   8 | Use this skill when authoring or integrating a Triton kernel in `python/sglang/jit_kernel/diffusion/triton/`.
   9 | We use a fused elementwise operation as the running example: `y = x * (1 + scale) + shift` (AdaLN modulation).
  10 | 
  11 | Before compiling, benchmarking, or profiling any Triton kernel from this guide, use `../sglang-diffusion-benchmark-profile/scripts/diffusion_skill_env.py` or the setup block in `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md` to `cd` to the repo root resolved from `sglang.__file__`, verify write access, export `FLASHINFER_DISABLE_VERSION_CHECK=1`, and choose an idle GPU.
  12 | 
  13 | ---
  14 | 
  15 | ## Directory Layout
  16 | 
  17 | ```
  18 | python/sglang/jit_kernel/diffusion/
  19 | ├── triton/
  20 | │   ├── scale_shift.py          # AdaLN scale/shift fused kernels
  21 | │   ├── norm.py                 # LayerNorm / RMSNorm fused kernels
  22 | │   ├── rmsnorm_onepass.py      # One-pass RMSNorm for small hidden size
  23 | │   └── rotary.py               # RoPE kernel
  24 | └── cutedsl/
  25 |     └── ...                     # CuTe DSL kernels (see existing-fast-paths.md in the benchmark/profile skill)
  26 | ```
  27 | 
  28 | New Triton kernels go into `triton/<op_name>.py`.
  29 | 
  30 | ---
  31 | 
  32 | ## Step 1: Write the Triton Kernel
  33 | 
  34 | Create `python/sglang/jit_kernel/diffusion/triton/<op_name>.py`.
  35 | 
  36 | ### 1a. Imports
  37 | 
  38 | ```python
  39 | import torch
  40 | import triton          # type: ignore
  41 | import triton.language as tl  # type: ignore
  42 | ```
  43 | 
  44 | Always use `# type: ignore` on triton imports — the stubs are incomplete.
  45 | 
  46 | ### 1b. The `@triton.jit` Kernel Function
  47 | 
  48 | Follow the naming convention `_<op_name>_kernel` (private, underscore prefix).
  49 | 
  50 | ```python
  51 | @triton.autotune(
  52 |     configs=[
  53 |         triton.Config({"BLOCK_C": 64},  num_warps=2),
  54 |         triton.Config({"BLOCK_C": 128}, num_warps=4),
  55 |         triton.Config({"BLOCK_C": 256}, num_warps=4),
  56 |         triton.Config({"BLOCK_C": 512}, num_warps=8),
  57 |     ],
  58 |     key=["C"],   # re-tune when hidden dim changes
  59 | )
  60 | @triton.jit
  61 | def _fused_scale_shift_kernel(
  62 |     # Pointers — always pass raw tensors; Triton takes .data_ptr() internally
  63 |     x_ptr,
  64 |     scale_ptr,
  65 |     shift_ptr,
  66 |     y_ptr,
  67 |     # Dimensions
  68 |     B,        # batch size
  69 |     L,        # sequence length
  70 |     C,        # hidden / channel dim
  71 |     # Strides — pass every stride separately; do NOT assume contiguous
  72 |     stride_xb, stride_xl, stride_xc,
  73 |     stride_sb, stride_sc,
  74 |     stride_yb, stride_yl, stride_yc,
  75 |     # Compile-time constants (tl.constexpr)
  76 |     BLOCK_C: tl.constexpr,
  77 | ):
  78 |     # Grid: (cdiv(L, 1), B) — one program per (batch, token)
  79 |     pid_l = tl.program_id(0)
  80 |     pid_b = tl.program_id(1)
  81 | 
  82 |     c_offs = tl.arange(0, BLOCK_C)
  83 |     mask   = c_offs < C
  84 | 
  85 |     x_row = pid_b * stride_xb + pid_l * stride_xl
  86 |     y_row = pid_b * stride_yb + pid_l * stride_yl
  87 |     s_row = pid_b * stride_sb
  88 | 
  89 |     x     = tl.load(x_ptr     + x_row + c_offs * stride_xc, mask=mask, other=0.0)
  90 |     scale = tl.load(scale_ptr + s_row + c_offs * stride_sc,  mask=mask, other=0.0)
  91 |     shift = tl.load(shift_ptr + s_row + c_offs * stride_sc,  mask=mask, other=0.0)
  92 | 
  93 |     y = x * (1.0 + scale) + shift
  94 |     tl.store(y_ptr + y_row + c_offs * stride_yc, y, mask=mask)
  95 | ```
  96 | 
  97 | **Rules:**
  98 | - All pointer arguments are raw (Triton extracts `.data_ptr()` internally when called via `kernel[grid](...)`).
  99 | - Pass every stride as a separate scalar — never assume a tensor is contiguous inside the kernel.
 100 | - Use `tl.constexpr` for block sizes and boolean flags (`HAS_RESIDUAL`, `IS_RMS_NORM`, etc.).
 101 | - Use `mask=mask, other=0.0` on every `tl.load` to avoid out-of-bounds reads.
 102 | - Compute in `tl.float32` when precision matters (`x.to(tl.float32)`), then cast back to output dtype before `tl.store`.
 103 | - Use `tl.fma(a, b, c)` (`a*b + c`) for fused multiply-add — avoids rounding errors and maps to a single instruction.
 104 | 
 105 | ### 1c. `@triton.autotune` Guidelines
 106 | 
 107 | | `key` entry | When to include |
 108 | |-------------|-----------------|
 109 | | `"C"` / `"hidden_dim"` | Always — block tile size depends on C |
 110 | | `"IS_RMS_NORM"` | When the kernel has a `constexpr` boolean flag that changes code paths |
 111 | | `"HAS_RESIDUAL"` | Same — constexpr path branching |
 112 | | Shape / batch / seq | Usually NOT — autotune cost outweighs benefit |
 113 | 
 114 | Keep configs in ascending `BLOCK_C` order with matching `num_warps` (warp × 32 threads ≤ 1024).
 115 | 
 116 | ### 1d. `torch.compile` Compatibility
 117 | 
 118 | When the kernel is called inside a `torch.compile`-d region, wrap the launch with `torch.library.wrap_triton`:
 119 | 
 120 | ```python
 121 | with torch.get_device_module().device(x.device):
 122 |     torch.library.wrap_triton(_fused_scale_shift_kernel)[grid](
 123 |         x, scale, shift, y,
 124 |         B, L, C,
 125 |         x.stride(0), x.stride(1), x.stride(2),
 126 |         scale.stride(0), scale.stride(1),
 127 |         y.stride(0), y.stride(1), y.stride(2),
 128 |     )
 129 | ```
 130 | 
 131 | Use `wrap_triton` when the kernel is called from a layer that runs under `torch.compile`.
 132 | Skip it for utility kernels called only at Python graph boundaries.
 133 | 
 134 | ---
 135 | 
 136 | ## Step 2: Write the Python Launcher
 137 | 
 138 | The launcher is a regular Python function (public, no underscore) in the same file.
 139 | 
 140 | ```python
 141 | def fused_scale_shift(
 142 |     x: torch.Tensor,
 143 |     scale: torch.Tensor,
 144 |     shift: torch.Tensor,
 145 | ) -> torch.Tensor:
 146 |     """
 147 |     Fused AdaLN modulation: y = x * (1 + scale) + shift.
 148 | 
 149 |     Args:
 150 |         x:     [B, L, C], CUDA, contiguous
 151 |         scale: [B, C],    CUDA
 152 |         shift: [B, C],    CUDA (same shape as scale)
 153 | 
 154 |     Returns:
 155 |         y: same shape and dtype as x
 156 |     """
 157 |     # --- Precondition checks ---
 158 |     assert x.is_cuda,           "x must be on CUDA"
 159 |     assert x.is_contiguous(),   "x must be contiguous"
 160 |     assert scale.is_cuda and shift.is_cuda
 161 |     assert x.ndim == 3,         f"x must be 3D [B, L, C], got {x.shape}"
 162 |     assert scale.shape == shift.shape
 163 |     B, L, C = x.shape
 164 | 
 165 |     # Allocate output
 166 |     y = torch.empty_like(x)
 167 | 
 168 |     # Grid: one program per token
 169 |     grid = (L, B)
 170 | 
 171 |     _fused_scale_shift_kernel[grid](
 172 |         x, scale, shift, y,
 173 |         B, L, C,
 174 |         x.stride(0),     x.stride(1),     x.stride(2),
 175 |         scale.stride(0), scale.stride(1),
 176 |         y.stride(0),     y.stride(1),     y.stride(2),
 177 |     )
 178 |     return y
 179 | ```
 180 | 
 181 | **Rules:**
 182 | - Validate CUDA placement and shape/dtype **before** launching — use `assert` with a helpful message.
 183 | - Call `.contiguous()` on inputs that the kernel requires contiguous **before** the launch, not inside it.
 184 | - Allocate the output with `torch.empty_like(x)` — never reuse input buffers unless the op is explicitly in-place.
 185 | - The `grid` is a tuple or a lambda `(META)` when block sizes are auto-tuned:
 186 | 
 187 | ```python
 188 | # Static grid (block size fixed)
 189 | grid = (triton.cdiv(L, BLOCK_L), triton.cdiv(C, BLOCK_C), B)
 190 | 
 191 | # Dynamic grid (block size comes from autotune)
 192 | grid = lambda META: (triton.cdiv(L, META["BLOCK_C"]), B)
 193 | ```
 194 | 
 195 | ### Handling Non-Contiguous Inputs
 196 | 
 197 | Never call `.contiguous()` silently — it copies data. Instead, pass strides to the kernel and let it handle arbitrary layouts. Only call `.contiguous()` when the kernel genuinely requires it (e.g., after a reshape):
 198 | 
 199 | ```python
 200 | # OK: reshape + contiguous needed for 2D view trick
 201 | x_2d = x.view(B * L, C)             # view only works on contiguous
 202 | if not x.is_contiguous():
 203 |     x = x.contiguous()
 204 |     x_2d = x.view(B * L, C)
 205 | ```
 206 | 
 207 | ---
 208 | 
 209 | ## Step 3: Integrate into the Layer
 210 | 
 211 | Call the new kernel from the appropriate layer file in
 212 | `python/sglang/multimodal_gen/runtime/layers/` (typically `layernorm.py` or `elementwise.py`).
 213 | 
 214 | ```python
 215 | # In layernorm.py or elementwise.py
 216 | import torch
 217 | 
 218 | def apply_scale_shift(x, scale, shift):
 219 |     if x.is_cuda:
 220 |         from sglang.jit_kernel.diffusion.triton.my_op import fused_scale_shift
 221 |         return fused_scale_shift(x, scale, shift)
 222 |     # Pure-PyTorch fallback for non-CUDA execution
 223 |     return x * (1.0 + scale) + shift
 224 | ```
 225 | 
 226 | **Rules:**
 227 | - Gate on `x.is_cuda` — the Triton kernel only runs on CUDA; the fallback handles everything else.
 228 | - The launcher raises `AssertionError` on invalid inputs (wrong shape, CPU tensor, etc.) — do **not** silently catch these. Let them propagate so bugs are visible during development.
 229 | - Add `logger.warning_once(...)` only when falling back due to a **known hardware limitation** (e.g., unsupported SM compute capability), not for wrong-input errors.
 230 | 
 231 | ---
 232 | 
 233 | ## Step 4: Write Tests
 234 | 
 235 | Create `python/sglang/jit_kernel/tests/test_<op_name>.py`.
 236 | 
 237 | ```python
 238 | import pytest
 239 | import torch
 240 | 
 241 | from sglang.jit_kernel.diffusion.triton.my_op import fused_scale_shift
 242 | 
 243 | 
 244 | def _ref_fused_scale_shift(x, scale, shift):
 245 |     """PyTorch reference implementation."""
 246 |     # Broadcast scale/shift from [B, C] to [B, L, C]
 247 |     return x * (1.0 + scale.unsqueeze(1)) + shift.unsqueeze(1)
 248 | 
 249 | 
 250 | @pytest.fixture(autouse=True)
 251 | def require_cuda():
 252 |     if not torch.cuda.is_available():
 253 |         pytest.skip("CUDA required")
 254 | 
 255 | 
 256 | @pytest.mark.parametrize("B,L,C", [
 257 |     (1, 6,    3072),   # Qwen (small batch)
 258 |     (1, 1024, 1536),   # Wan
 259 |     (2, 512,  3072),   # typical training shape
 260 |     (1, 1,    256),    # edge: L=1
 261 | ])
 262 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 263 | def test_fused_scale_shift_correctness(B, L, C, dtype):
 264 |     torch.manual_seed(0)
 265 |     x     = torch.randn(B, L, C, dtype=dtype, device="cuda")
 266 |     scale = torch.randn(B, C,    dtype=dtype, device="cuda") * 0.1
 267 |     shift = torch.randn(B, C,    dtype=dtype, device="cuda") * 0.1
 268 | 
 269 |     out = fused_scale_shift(x, scale, shift)
 270 |     ref = _ref_fused_scale_shift(x.float(), scale.float(), shift.float()).to(dtype)
 271 | 
 272 |     atol = 1e-5 if dtype == torch.float32 else 1e-2
 273 |     torch.testing.assert_close(out, ref, atol=atol, rtol=atol,
 274 |                                 msg=f"Mismatch at B={B} L={L} C={C} dtype={dtype}")
 275 | 
 276 | 
 277 | def test_fused_scale_shift_non_cuda_raises():
 278 |     x     = torch.randn(1, 4, 64)
 279 |     scale = torch.randn(1, 64)
 280 |     shift = torch.randn(1, 64)
 281 |     with pytest.raises(AssertionError, match="CUDA"):
 282 |         fused_scale_shift(x, scale, shift)
 283 | 
 284 | 
 285 | def test_fused_scale_shift_output_dtype_preserved():
 286 |     x     = torch.randn(1, 8, 128, dtype=torch.bfloat16, device="cuda")
 287 |     scale = torch.randn(1, 128, dtype=torch.bfloat16, device="cuda")
 288 |     shift = torch.zeros(1, 128, dtype=torch.bfloat16, device="cuda")
 289 |     out   = fused_scale_shift(x, scale, shift)
 290 |     assert out.dtype == torch.bfloat16
 291 |     assert out.shape == x.shape
 292 | 
 293 | 
 294 | if __name__ == "__main__":
 295 |     import sys
 296 |     sys.exit(pytest.main([__file__, "-v"]))
 297 | ```
 298 | 
 299 | Run:
 300 | 
 301 | ```bash
 302 | pytest python/sglang/jit_kernel/tests/test_<op_name>.py -v
 303 | ```
 304 | 
 305 | **Test coverage requirements:**
 306 | 1. Reference comparison against pure-PyTorch for all supported dtypes (fp16, bf16, fp32).
 307 | 2. Edge shapes: `L=1`, `C` not a multiple of the largest BLOCK_C, large `B`.
 308 | 3. Error cases: CPU tensor, wrong shape.
 309 | 4. Output dtype and shape preservation.
 310 | 
 311 | ---
 312 | 
 313 | ## Step 5: Add a Benchmark (required)
 314 | 
 315 | Create `python/sglang/jit_kernel/benchmark/bench_<op_name>.py`.
 316 | 
 317 | ```python
 318 | import torch
 319 | import triton.testing
 320 | 
 321 | from sglang.jit_kernel.diffusion.triton.my_op import fused_scale_shift
 322 | 
 323 | 
 324 | SHAPES = [
 325 |     # (B, L, C)  — representative diffusion shapes
 326 |     (1, 6,    3072),   # Qwen image
 327 |     (1, 1024, 1536),   # Wan video
 328 |     (1, 4096, 3072),   # FLUX double-stream
 329 | ]
 330 | 
 331 | 
 332 | @triton.testing.perf_report(
 333 |     triton.testing.Benchmark(
 334 |         x_names=["B", "L", "C"],
 335 |         x_vals=SHAPES,
 336 |         line_arg="provider",
 337 |         line_vals=["triton", "torch"],
 338 |         line_names=["Triton Fused", "PyTorch"],
 339 |         styles=[("blue", "-"), ("red", "--")],
 340 |         ylabel="µs (median)",
 341 |         plot_name="fused-scale-shift",
 342 |         args={},
 343 |     )
 344 | )
 345 | def benchmark(B, L, C, provider):
 346 |     dtype = torch.bfloat16
 347 |     x     = torch.randn(B, L, C, dtype=dtype, device="cuda")
 348 |     scale = torch.randn(B, C,    dtype=dtype, device="cuda")
 349 |     shift = torch.randn(B, C,    dtype=dtype, device="cuda")
 350 | 
 351 |     if provider == "triton":
 352 |         fn = lambda: fused_scale_shift(x, scale, shift)
 353 |     else:
 354 |         fn = lambda: x * (1.0 + scale.unsqueeze(1)) + shift.unsqueeze(1)
 355 | 
 356 |     ms, *_ = triton.testing.do_bench_cudagraph(fn, quantiles=[0.5, 0.2, 0.8])
 357 |     return ms * 1000  # µs
 358 | 
 359 | 
 360 | if __name__ == "__main__":
 361 |     benchmark.run(print_data=True)
 362 | ```
 363 | 
 364 | Run:
 365 | 
 366 | ```bash
 367 | python python/sglang/jit_kernel/benchmark/bench_<op_name>.py
 368 | ```
 369 | 
 370 | ---
 371 | 
 372 | ## Step 6: Profile with Nsight Compute (required for optimization work)
 373 | 
 374 | After correctness tests, you must use **ncu (Nsight Compute)** to validate hardware efficiency (bandwidth/throughput/occupancy/bottleneck type).
 375 | 
 376 | To avoid duplicating ncu CLI details across multiple skills, this skill does not repeat command flags. Follow the canonical docs:
 377 | 
 378 | - `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md` → Step 3.5 (ncu workflow, including CUDA graph profiling)
 379 | - `../sglang-diffusion-benchmark-profile/nsight-profiler.md` (metrics interpretation: bandwidth / occupancy / roofline / warp stalls)
 380 | 
 381 | ---
 382 | 
 383 | ## Common Patterns Reference
 384 | 
 385 | ### Pattern 1: Autotune over a 2D tile (L × C)
 386 | 
 387 | Used in `scale_shift.py` (`fuse_scale_shift_kernel_blc_opt`):
 388 | 
 389 | ```python
 390 | @triton.jit
 391 | def _kernel(..., BLOCK_L: tl.constexpr, BLOCK_C: tl.constexpr):
 392 |     pid_l = tl.program_id(0)
 393 |     pid_c = tl.program_id(1)
 394 |     pid_b = tl.program_id(2)
 395 |     l_offs = pid_l * BLOCK_L + tl.arange(0, BLOCK_L)
 396 |     c_offs = pid_c * BLOCK_C + tl.arange(0, BLOCK_C)
 397 |     mask = (l_offs[:, None] < L) & (c_offs[None, :] < C)
 398 |     ...
 399 | 
 400 | # Launch:
 401 | grid = (triton.cdiv(L, BLOCK_L), triton.cdiv(C, BLOCK_C), B)
 402 | _kernel[grid](..., BLOCK_L=block_l, BLOCK_C=block_c, num_warps=4, num_stages=2)
 403 | ```
 404 | 
 405 | ### Pattern 2: One-pass RMSNorm for small hidden size
 406 | 
 407 | Used in `rmsnorm_onepass.py`:
 408 | 
 409 | ```python
 410 | @triton.jit
 411 | def _rms_norm_tiled_onepass(y_ptr, x_ptr, w_ptr,
 412 |                               SEQ: tl.constexpr, DIM: tl.constexpr, EPS: tl.constexpr,
 413 |                               BLOCK_SIZE_SEQ: tl.constexpr, BLOCK_SIZE_DIM: tl.constexpr):
 414 |     seq_blk_id = tl.program_id(0)
 415 |     seq_id     = seq_blk_id * BLOCK_SIZE_SEQ
 416 |     seq_offset = seq_id + tl.arange(0, BLOCK_SIZE_SEQ)[:, None]
 417 |     d_offset   = tl.arange(0, BLOCK_SIZE_DIM)[None, :]
 418 |     ...
 419 |     x = tl.load(x_ptr + seq_offset * DIM + d_offset, mask=..., other=0.0).to(tl.float32)
 420 |     mean_sq = tl.sum(x * x, axis=1, keep_dims=True) / DIM
 421 |     rstd    = tl.math.rsqrt(mean_sq + EPS)
 422 |     tl.store(y_ptr + ..., x * rstd * w, mask=...)
 423 | 
 424 | # Launch with wrap_triton for torch.compile compat:
 425 | with torch.get_device_module().device(x.device):
 426 |     torch.library.wrap_triton(_rms_norm_tiled_onepass)[grid](
 427 |         y_view, x_view, w,
 428 |         S, D, eps,
 429 |         BLOCK_SIZE_DIM=triton.next_power_of_2(D),
 430 |         BLOCK_SIZE_SEQ=BLOCK_SIZE_SEQ,
 431 |     )
 432 | ```
 433 | 
 434 | ### Pattern 3: `tl.constexpr` boolean flags for conditional paths
 435 | 
 436 | Used in `norm.py` and `scale_shift.py`:
 437 | 
 438 | ```python
 439 | @triton.jit
 440 | def _kernel(...,
 441 |             IS_RMS_NORM:   tl.constexpr,
 442 |             HAS_RESIDUAL:  tl.constexpr,
 443 |             SCALE_IS_SCALAR: tl.constexpr):
 444 |     ...
 445 |     if IS_RMS_NORM:
 446 |         var = tl.sum(x * x, axis=0) / N
 447 |     else:
 448 |         mean = tl.sum(x, axis=0) / N
 449 |         var  = tl.sum((x - mean) ** 2, axis=0) / N
 450 | 
 451 |     if HAS_RESIDUAL:
 452 |         x = x + tl.load(residual_ptr + ...)
 453 | 
 454 |     if SCALE_IS_SCALAR:
 455 |         scale_val = tl.load(scale_ptr)
 456 |         scale = tl.full([BLOCK_N], scale_val, dtype=scale_val.dtype)
 457 |     else:
 458 |         scale = tl.load(scale_ptr + col_offsets, mask=mask, other=0.0)
 459 | ```
 460 | 
 461 | Autotune key must include these booleans so the compiler generates separate specializations.
 462 | 
 463 | ### Pattern 4: Computing in fp32, storing in original dtype
 464 | 
 465 | Always up-cast to `tl.float32` for reductions and math, then down-cast before storing:
 466 | 
 467 | ```python
 468 | x_f32    = x.to(tl.float32)
 469 | scale_f32 = scale.to(tl.float32)
 470 | y_f32    = x_f32 * (1.0 + scale_f32) + shift_f32
 471 | tl.store(y_ptr + offsets, y_f32.to(x.dtype), mask=mask)
 472 | ```
 473 | 
 474 | ---
 475 | 
 476 | ## Checklist Before Submitting
 477 | 
 478 | ### Prerequisites
 479 | - [ ] `ncu --version` prints a valid Nsight Compute version (required for Step 7 profiling)
 480 | 
 481 | ### Implementation
 482 | - [ ] Kernel file at `python/sglang/jit_kernel/diffusion/triton/<op_name>.py`
 483 | - [ ] All pointer arguments passed with separate stride scalars
 484 | - [ ] Every `tl.load` uses `mask=` and `other=`
 485 | - [ ] Autotune `key` includes all `constexpr` flags that change code paths
 486 | - [ ] `torch.library.wrap_triton` used if kernel runs inside `torch.compile` region
 487 | - [ ] PyTorch fallback path in the layer integration (see Step 4)
 488 | 
 489 | ### Validation
 490 | - [ ] Tests pass: `pytest python/sglang/jit_kernel/tests/test_<op_name>.py -v`
 491 | - [ ] Benchmark runs: `python python/sglang/jit_kernel/benchmark/bench_<op_name>.py`
 492 | - [ ] **Correctness verified**: Triton output matches PyTorch reference within tolerance
 493 | - [ ] Nsight Compute profile collected (`ncu --set full`); achieved occupancy ≥ 50% and memory throughput ≥ 70% of peak (or bottleneck documented)
 494 | 
 495 | ---
 496 | 
 497 | ## Summary of Files Created/Modified
 498 | 
 499 | ```
 500 | python/sglang/jit_kernel/diffusion/triton/<op_name>.py      # NEW: Triton kernel + launcher
 501 | python/sglang/jit_kernel/tests/test_<op_name>.py            # NEW: correctness tests
 502 | python/sglang/jit_kernel/benchmark/bench_<op_name>.py       # NEW: performance benchmark
 503 | python/sglang/multimodal_gen/runtime/layers/layernorm.py    # MODIFIED: integrate into layer
 504 |   (or elementwise.py, depending on op type)
 505 | ```
 506 | 
 507 | ## References
 508 | 
 509 | - `python/sglang/jit_kernel/diffusion/triton/scale_shift.py` — 2D tile pattern, scalar broadcast, 4D shape handling
 510 | - `python/sglang/jit_kernel/diffusion/triton/rmsnorm_onepass.py` — `wrap_triton`, tiled one-pass reduction
 511 | - `python/sglang/jit_kernel/diffusion/triton/norm.py` — complex autotune with many `constexpr` flags
 512 | - `python/sglang/jit_kernel/diffusion/triton/rotary.py` — per-head grid, interleaved RoPE
 513 | - `../sglang-diffusion-benchmark-profile/nsight-profiler.md` — full Nsight Compute guide: occupancy analysis, roofline model, warp efficiency, kernel comparison
 514 | - `../sglang-diffusion-benchmark-profile/benchmark-and-profile.md` — how to verify the kernel's impact on denoise latency
 515 | - `../sglang-diffusion-benchmark-profile/existing-fast-paths.md` — overview of existing fused kernel entry points
```


---
## python/sglang/multimodal_gen/README.md

```
   1 | <div align="center"  style="display:block; margin:auto;">
   2 | <img src=https://github.com/lm-sys/lm-sys.github.io/releases/download/test/sgl-diffusion-logo.png width="80%"/>
   3 | </div>
   4 | 
   5 | **SGLang diffusion is an inference framework for accelerated image/video generation.**
   6 | 
   7 | SGLang diffusion features an end-to-end unified pipeline for accelerating diffusion models. It is designed to be modular and extensible, allowing users to easily add new models and optimizations.
   8 | 
   9 | ## Key Features
  10 | 
  11 | SGLang Diffusion has the following features:
  12 |   - Broad model support: Wan series, FastWan series, Hunyuan, Qwen-Image, Qwen-Image-Edit, Flux, Z-Image, GLM-Image
  13 |   - Fast inference speed: enpowered by highly optimized kernel from sgl-kernel and efficient scheduler loop
  14 |   - Ease of use: OpenAI-compatible api, CLI, and python sdk support
  15 |   - Multi-platform support:
  16 |     - NVIDIA GPUs (H100, H200, A100, B200, 4090)
  17 |     - AMD GPUs (MI300X, MI325X)
  18 |     - Ascend NPU (A2, A3)
  19 |     - Apple Silicon (M-series via MPS)
  20 |     - Moore Threads GPUs (MTT S5000)
  21 | 
  22 | ### AMD/ROCm Support
  23 | 
  24 | SGLang Diffusion supports AMD Instinct GPUs through ROCm. On AMD platforms, we use the Triton attention backend and leverage AITER kernels for optimized layernorm and other operations. See the [installation guide](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/installation.md) for setup instructions.
  25 | 
  26 | ### Moore Threads/MUSA Support
  27 | 
  28 | SGLang Diffusion supports Moore Threads GPUs (MTGPU) through the MUSA software stack. On MUSA platforms, we use the Torch SDPA backend for attention. See the [installation guide](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/installation.md) for setup instructions.
  29 | 
  30 | ### Apple MPS Support
  31 | 
  32 | SGLang Diffusion supports Apple Silicon (M-series) via the MPS backend. Since Triton is Linux-only, all Triton kernels are replaced with PyTorch-native fallbacks on MPS. Norm operations can be optionally accelerated with MLX fused Metal kernels (`SGLANG_USE_MLX=1`). See the [installation guide](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/installation.md) for setup instructions.
  33 | 
  34 | ## Getting Started
  35 | 
  36 | ```bash
  37 | uv pip install 'sglang[diffusion]' --prerelease=allow
  38 | ```
  39 | 
  40 | For more installation methods (e.g. pypi, uv, docker, ROCm/AMD, MUSA/Moore Threads), check [install.md](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/installation.md).
  41 | 
  42 | ## Inference
  43 | 
  44 | Here's a minimal example to generate a video using the default settings:
  45 | 
  46 | ```python
  47 | from sglang.multimodal_gen import DiffGenerator
  48 | 
  49 | def main():
  50 |     # Create a diff generator from a pre-trained model
  51 |     generator = DiffGenerator.from_pretrained(
  52 |         model_path="Wan-AI/Wan2.1-T2V-1.3B-Diffusers",
  53 |         num_gpus=1,  # Adjust based on your hardware
  54 |     )
  55 | 
  56 |     # Generate the video
  57 |     video = generator.generate(
  58 |         sampling_params_kwargs=dict(
  59 |             prompt="A curious raccoon peers through a vibrant field of yellow sunflowers, its eyes wide with interest.",
  60 |             return_frames=True,  # Also return frames from this call (defaults to False)
  61 |             output_path="my_videos/",  # Controls where videos are saved
  62 |             save_output=True
  63 |         )
  64 |     )
  65 | 
  66 | if __name__ == '__main__':
  67 |     main()
  68 | ```
  69 | 
  70 | Or, more simply, with the CLI:
  71 | 
  72 | ```bash
  73 | sglang generate --model-path Wan-AI/Wan2.1-T2V-1.3B-Diffusers \
  74 |     --text-encoder-cpu-offload --pin-cpu-memory \
  75 |     --prompt "A curious raccoon" \
  76 |     --save-output
  77 | ```
  78 | 
  79 | ### LoRA support
  80 | 
  81 | Apply LoRA adapters via `--lora-path`:
  82 | 
  83 | ```bash
  84 | sglang generate \
  85 |   --model-path Qwen/Qwen-Image-Edit-2511 \
  86 |   --lora-path prithivMLmods/Qwen-Image-Edit-2511-Anime \
  87 |   --prompt "Transform into anime." \
  88 |   --image-path "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png" \
  89 |   --save-output
  90 | ```
  91 | 
  92 | For more usage examples (e.g. OpenAI compatible API, server mode), check [cli.md](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/api/cli.md).
  93 | 
  94 | ## Contributing
  95 | 
  96 | All contributions are welcome. The contribution guide is available [here](https://github.com/sgl-project/sglang/tree/main/docs/diffusion/contributing.md).
  97 | 
  98 | ## Acknowledgement
  99 | 
 100 | We learnt and reused code from the following projects:
 101 | 
 102 | - [FastVideo](https://github.com/hao-ai-lab/FastVideo.git). The major components of this repo are based on a fork of FastVideo on Sept. 24, 2025.
 103 | - [xDiT](https://github.com/xdit-project/xDiT). We used the parallelism library from it.
 104 | - [diffusers](https://github.com/huggingface/diffusers) We used the pipeline design from it.
```
