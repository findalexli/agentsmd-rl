# Agent Config Files for sglang-lscpu-topology-fix

Repo: sgl-project/sglang
Commit: 069c7e4188aca6ef69c0b81dfa05abba49685946
Files found: 13


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
  14 | - Input: tensor `x` (CUDA) and scalar `factor` (float, passed as C++ template argument)
  15 | - Output: `x * factor` (element-wise), allocated internally
  16 | - Supported dtypes: **FP16 (`torch.float16`), BF16 (`torch.bfloat16`), FP32 (`torch.float32`)**
  17 | 
  18 | ## When to use JIT vs AOT (`sgl-kernel`)
  19 | 
  20 | - **JIT (`jit_kernel`)**: lightweight, few dependencies, rapid iteration, compiled on first use
  21 | - **AOT (`sgl-kernel`)**: depends on CUTLASS / FlashInfer / DeepGEMM, needs pre-built wheel
  22 | 
  23 | ---
  24 | 
  25 | ## Common Abstractions in `python/sglang/jit_kernel/include/sgl_kernel/`
  26 | 
  27 | **Always prefer these abstractions over raw CUDA primitives.** They provide safety, readability, and consistency with the rest of the codebase.
  28 | 
  29 | ### `utils.h` — Host-side utilities
  30 | 
  31 | ```cpp
  32 | #include <sgl_kernel/utils.h>
  33 | ```
  34 | 
  35 | - **`host::RuntimeCheck(cond, args...)`** — Assert a condition at runtime; throws `PanicError` with file/line info on failure. Prefer this over bare `assert`.
  36 | - **`host::Panic(args...)`** — Unconditionally throw a `PanicError` with a descriptive message.
  37 | - **`host::div_ceil(a, b)`** — Integer ceiling division `(a + b - 1) / b`.
  38 | - **`host::irange(n)`** / **`host::irange(start, end)`** — Range views for cleaner loops.
  39 | - **`host::pointer::offset(ptr, offsets...)`** — Byte-safe pointer arithmetic on `void*`. Use this instead of raw casts.
  40 | 
  41 | ### `utils.cuh` — Device-side utilities + `LaunchKernel`
  42 | 
  43 | ```cpp
  44 | #include <sgl_kernel/utils.cuh>
  45 | ```
  46 | 
  47 | - **Type aliases**: `fp16_t`, `bf16_t`, `fp32_t`, `fp8_e4m3_t`, `fp8_e5m2_t` and their packed variants `fp16x2_t`, `bf16x2_t`, `fp32x2_t`, etc.
  48 | - **`SGL_DEVICE`** — Expands to `__forceinline__ __device__`. Use on all device functions.
  49 | - **`device::kWarpThreads`** — Constant `32`.
  50 | - **`device::load_as<T>(ptr, offset)`** / **`device::store_as<T>(ptr, val, offset)`** — Type-safe loads/stores from `void*`.
  51 | - **`device::pointer::offset(ptr, offsets...)`** — Pointer arithmetic on device.
  52 | - **`host::LaunchKernel(grid, block, device_or_stream [, smem])`** — RAII kernel launcher that:
  53 |   - Resolves the CUDA stream from a `DLDevice` via TVM-FFI automatically.
  54 |   - Checks the CUDA error with file/line info after launch via `operator()(kernel, args...)`.
  55 |   - Supports `.enable_pdl(bool)` for PDL (Programmatic Dependent Launch, SM90+).
  56 | - **`host::RuntimeDeviceCheck(cudaError_t)`** — Check a CUDA error; throw on failure.
  57 | 
  58 | ### `tensor.h` — Tensor validation (`TensorMatcher`, Symbolic types)
  59 | 
  60 | ```cpp
  61 | #include <sgl_kernel/tensor.h>
  62 | ```
  63 | 
  64 | This is the **primary validation API** for all kernel launchers. Use it to validate every `tvm::ffi::TensorView` argument.
  65 | 
  66 | - **`host::SymbolicSize{"name"}`** — A named symbolic dimension. Call `.set_value(n)` to pin it, `.unwrap()` to extract after verification.
  67 | - **`host::SymbolicDType`** — Symbolic dtype. Use `.set_options<Ts...>()` to restrict allowed types.
  68 | - **`host::SymbolicDevice`** — Symbolic device. Use `.set_options<kDLCUDA>()` to restrict to CUDA.
  69 | - **`host::TensorMatcher({dims...})`** — Fluent builder for tensor validation:
  70 |   - `.with_dtype<T>()` — require a specific C++ type (e.g. `fp16_t`)
  71 |   - `.with_dtype<T1, T2, ...>()` — allow a set of types
  72 |   - `.with_device<kDLCUDA>(device_sym)` — require CUDA, bind device to symbol
  73 |   - `.with_strides({strides...})` — validate strides (omit to require contiguous)
  74 |   - `.verify(tensor_view)` — execute the check; throws `PanicError` with full context on failure; **chainable** (`verify(a).verify(b)` to check multiple tensors with the same shape)
  75 | 
  76 | **Typical pattern:**
  77 | ```cpp
  78 | auto N = SymbolicSize{"num_elements"};
  79 | auto device = SymbolicDevice{};
  80 | device.set_options<kDLCUDA>();
  81 | TensorMatcher({N})  //
  82 |     .with_dtype<fp16_t>()
  83 |     .with_device(device)
  84 |     .verify(dst)
  85 |     .verify(src);  // same shape, dtype, device as dst
  86 | const size_t n = N.unwrap();
  87 | const DLDevice dev = device.unwrap();
  88 | ```
  89 | 
  90 | ### `type.cuh` — `dtype_trait<T>` and `packed_t<T>`
  91 | 
  92 | ```cpp
  93 | #include <sgl_kernel/type.cuh>
  94 | ```
  95 | 
  96 | - **`dtype_trait<T>`** — Static trait struct for each scalar type. Provides:
  97 |   - `dtype_trait<T>::from(value)` — convert from another type (e.g. `fp32_t` → `fp16_t`)
  98 |   - `dtype_trait<T>::abs/sqrt/rsqrt/max/min(x)` — type-dispatched math (for `fp32_t`)
  99 | - **`packed_t<T>`** — Two-element packed alias: `packed_t<fp16_t>` = `fp16x2_t`, `packed_t<bf16_t>` = `bf16x2_t`, `packed_t<fp32_t>` = `fp32x2_t`. Use for vectorized loads/stores.
 100 | - **`device::cast<To, From>(value)`** — Type-safe cast using `dtype_trait`, e.g. `cast<fp32x2_t, fp16x2_t>(v)`.
 101 | 
 102 | ### `vec.cuh` — Vectorized memory access (`AlignedVector`)
 103 | 
 104 | ```cpp
 105 | #include <sgl_kernel/vec.cuh>
 106 | ```
 107 | 
 108 | - **`device::AlignedVector<T, N>`** — Aligned storage for N elements of type T. N must be a power of two, `sizeof(T)*N <= 32`. Enables 128-bit vector loads/stores for bandwidth efficiency.
 109 |   - `.load(ptr, offset)` — vectorized load from `ptr[offset]`
 110 |   - `.store(ptr, offset)` — vectorized store to `ptr[offset]`
 111 |   - `.fill(value)` — fill all lanes
 112 |   - `operator[](i)` — element access
 113 | 
 114 | ### `tile.cuh` — `tile::Memory` (strided memory access pattern)
 115 | 
 116 | ```cpp
 117 | #include <sgl_kernel/tile.cuh>
 118 | ```
 119 | 
 120 | - **`device::tile::Memory<T>::cta(blockDim.x)`** — Creates a tile accessor where each thread handles `tid = threadIdx.x` with stride `blockDim.x`. Common for loops over a 1D array.
 121 | - **`.load(ptr, offset)`** — loads `ptr[tid + offset * blockDim.x]`
 122 | - **`.store(ptr, val, offset)`** — stores to `ptr[tid + offset * blockDim.x]`
 123 | - **`.in_bound(n, offset)`** — boundary check
 124 | 
 125 | ### `math.cuh` — Device math (`device::math::`)
 126 | 
 127 | ```cpp
 128 | #include <sgl_kernel/math.cuh>
 129 | ```
 130 | 
 131 | - `device::math::max/min/abs/sqrt/rsqrt<T>(a, b)` — type-dispatched math via `dtype_trait`
 132 | - `device::math::exp/sin/cos(float)` — fast float math wrappers
 133 | 
 134 | ### `warp.cuh` — Warp-level primitives
 135 | 
 136 | ```cpp
 137 | #include <sgl_kernel/warp.cuh>
 138 | ```
 139 | 
 140 | - `device::warp::reduce_sum<T>(value)` — warp-level sum reduction via `__shfl_xor_sync`
 141 | - `device::warp::reduce_max<T>(value)` — warp-level max reduction
 142 | 
 143 | ### `cta.cuh` — CTA-level primitives
 144 | 
 145 | ```cpp
 146 | #include <sgl_kernel/cta.cuh>
 147 | ```
 148 | 
 149 | - `device::cta::reduce_max<T>(value, smem, min_value)` — CTA-wide max using shared memory + warp reduction. Caller is responsible for a `__syncthreads()` after if the result in `smem[0]` is needed.
 150 | 
 151 | ### `atomic.cuh` — Atomic operations
 152 | 
 153 | ```cpp
 154 | #include <sgl_kernel/atomic.cuh>
 155 | ```
 156 | 
 157 | - `device::atomic::max(float* addr, float value)` — float atomic max (handles negative values correctly via bit tricks).
 158 | 
 159 | ### `runtime.cuh` — Occupancy and device info
 160 | 
 161 | ```cpp
 162 | #include <sgl_kernel/runtime.cuh>
 163 | ```
 164 | 
 165 | - `host::runtime::get_blocks_per_sm(kernel, block_dim)` — max active blocks per SM (occupancy)
 166 | - `host::runtime::get_sm_count(device_id)` — number of SMs on the device
 167 | - `host::runtime::get_cc_major(device_id)` — compute capability major version
 168 | 
 169 | **Persistent kernel pattern** (cap blocks to SM count × occupancy):
 170 | ```cpp
 171 | static const uint32_t max_occ = runtime::get_blocks_per_sm(kernel, kBlockSize);
 172 | static const uint32_t num_sm  = runtime::get_sm_count(device.unwrap().device_id);
 173 | const auto num_blocks = std::min(num_sm * max_occ, div_ceil(n, kBlockSize));
 174 | LaunchKernel(num_blocks, kBlockSize, device.unwrap())(kernel, params);
 175 | ```
 176 | 
 177 | ---
 178 | 
 179 | ## Step 0 (optional): Generate a `.clangd` config for better IDE support
 180 | 
 181 | ```bash
 182 | python -m sglang.jit_kernel
 183 | ```
 184 | 
 185 | ---
 186 | 
 187 | ## Step 1: Implement the CUDA kernel in `jit_kernel/csrc/`
 188 | 
 189 | Create `python/sglang/jit_kernel/csrc/elementwise/scale.cuh`.
 190 | 
 191 | The implementation fully uses the project abstractions described above:
 192 | 
 193 | ```cpp
 194 | #include <sgl_kernel/tensor.h>   // TensorMatcher, SymbolicSize, SymbolicDevice
 195 | #include <sgl_kernel/type.cuh>   // dtype_trait, fp16_t, bf16_t, fp32_t
 196 | #include <sgl_kernel/utils.h>    // RuntimeCheck, div_ceil
 197 | #include <sgl_kernel/utils.cuh>  // LaunchKernel, SGL_DEVICE
 198 | #include <sgl_kernel/vec.cuh>    // AlignedVector
 199 | 
 200 | #include <dlpack/dlpack.h>
 201 | #include <tvm/ffi/container/tensor.h>
 202 | 
 203 | namespace {
 204 | 
 205 | // ----------------------------------------------------------------
 206 | // Kernel: element-wise scale using vectorized 128-bit loads/stores
 207 | // T       = fp16_t | bf16_t | fp32_t
 208 | // kVecN   = number of elements per vector load (e.g. 8 for fp16)
 209 | // kFactor = scale factor encoded as kFactorNumer / kFactorDenom
 210 | // ----------------------------------------------------------------
 211 | template <typename T, int kVecN, int32_t kFactorNumer, int32_t kFactorDenom>
 212 | __global__ void scale_kernel(T* __restrict__ dst,
 213 |                               const T* __restrict__ src,
 214 |                               uint32_t n_vecs,
 215 |                               uint32_t n_remainder,
 216 |                               uint32_t n_total) {
 217 |   constexpr float kFactor = static_cast<float>(kFactorNumer)
 218 |                           / static_cast<float>(kFactorDenom);
 219 | 
 220 |   using vec_t = device::AlignedVector<T, kVecN>;
 221 | 
 222 |   // --- vectorised body ---
 223 |   const uint32_t vec_stride = blockDim.x * gridDim.x;
 224 |   for (uint32_t vi = blockIdx.x * blockDim.x + threadIdx.x;
 225 |        vi < n_vecs;
 226 |        vi += vec_stride) {
 227 |     vec_t v;
 228 |     v.load(src, vi);
 229 | #pragma unroll
 230 |     for (int i = 0; i < kVecN; ++i) {
 231 |       v[i] = static_cast<T>(static_cast<float>(v[i]) * kFactor);
 232 |     }
 233 |     v.store(dst, vi);
 234 |   }
 235 | 
 236 |   // --- scalar tail ---
 237 |   const uint32_t base = n_vecs * kVecN;
 238 |   const uint32_t scalar_stride = blockDim.x * gridDim.x;
 239 |   for (uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
 240 |        i < n_remainder;
 241 |        i += scalar_stride) {
 242 |     dst[base + i] = static_cast<T>(static_cast<float>(src[base + i]) * kFactor);
 243 |   }
 244 | }
 245 | 
 246 | // ----------------------------------------------------------------
 247 | // Launcher: validates tensors, selects vector width, launches kernel
 248 | // ----------------------------------------------------------------
 249 | template <typename T, int32_t kFactorNumer, int32_t kFactorDenom>
 250 | void scale(tvm::ffi::TensorView dst, tvm::ffi::TensorView src) {
 251 |   using namespace host;
 252 | 
 253 |   // 1. Validate input tensors with TensorMatcher
 254 |   SymbolicSize N = {"num_elements"};
 255 |   SymbolicDevice device_;
 256 |   device_.set_options<kDLCUDA>();
 257 | 
 258 |   TensorMatcher({N})  //
 259 |       .with_dtype<T>()
 260 |       .with_device(device_)
 261 |       .verify(dst)
 262 |       .verify(src);  // same shape / dtype / device as dst
 263 | 
 264 |   const uint32_t n         = static_cast<uint32_t>(N.unwrap());
 265 |   const DLDevice device    = device_.unwrap();
 266 | 
 267 |   RuntimeCheck(n > 0, "scale: num_elements must be > 0, got ", n);
 268 | 
 269 |   // 2. Choose vector width for 128-bit loads (16 bytes)
 270 |   //    fp16/bf16: 8 elements × 2 bytes = 16 bytes
 271 |   //    fp32:      4 elements × 4 bytes = 16 bytes
 272 |   constexpr int kVecN    = 16 / sizeof(T);
 273 |   const uint32_t n_vecs      = n / kVecN;
 274 |   const uint32_t n_remainder = n % kVecN;
 275 | 
 276 |   // 3. Launch
 277 |   constexpr uint32_t kBlockSize = 256;
 278 |   const uint32_t grid           = div_ceil(std::max(n_vecs, n_remainder), kBlockSize);
 279 | 
 280 |   LaunchKernel(grid, kBlockSize, device)(
 281 |       scale_kernel<T, kVecN, kFactorNumer, kFactorDenom>,
 282 |       static_cast<T*>(dst.data_ptr()),
 283 |       static_cast<const T*>(src.data_ptr()),
 284 |       n_vecs,
 285 |       n_remainder,
 286 |       n);
 287 | }
 288 | 
 289 | }  // namespace
 290 | ```
 291 | 
 292 | **Key points:**
 293 | 
 294 | - Include headers from `sgl_kernel/` — **not** raw CUDA headers for anything already covered
 295 | - Use `TensorMatcher` for all tensor validation; never manually check shape/dtype/device
 296 | - Use `AlignedVector` for vectorised 128-bit loads/stores — significant bandwidth win
 297 | - Use `LaunchKernel` — it resolves the stream and checks errors automatically
 298 | - Use `RuntimeCheck` for runtime assertions with useful error messages
 299 | - `fp16_t` / `bf16_t` / `fp32_t` are the project's type aliases (from `utils.cuh`)
 300 | - `device::cast<To, From>` or `dtype_trait<T>::from(val)` for cross-type conversions
 301 | - `device::math::` functions for device math instead of bare `__` intrinsics
 302 | 
 303 | ---
 304 | 
 305 | ## Step 2: Add the Python wrapper in `jit_kernel/`
 306 | 
 307 | Create `python/sglang/jit_kernel/scale.py`:
 308 | 
 309 | ```python
 310 | from __future__ import annotations
 311 | 
 312 | from typing import TYPE_CHECKING
 313 | 
 314 | import torch
 315 | 
 316 | from sglang.jit_kernel.utils import cache_once, load_jit, make_cpp_args
 317 | 
 318 | if TYPE_CHECKING:
 319 |     from tvm_ffi.module import Module
 320 | 
 321 | 
 322 | @cache_once
 323 | def _jit_scale_module(dtype: torch.dtype, factor_numer: int, factor_denom: int) -> Module:
 324 |     """Compile and cache the JIT scale module for a given dtype and factor."""
 325 |     args = make_cpp_args(dtype, factor_numer, factor_denom)
 326 |     return load_jit(
 327 |         "scale",
 328 |         *args,
 329 |         cuda_files=["elementwise/scale.cuh"],
 330 |         cuda_wrappers=[("scale", f"scale<{args}>")],
 331 |     )
 332 | 
 333 | 
 334 | def scale(src: torch.Tensor, factor: float, out: torch.Tensor | None = None) -> torch.Tensor:
 335 |     """
 336 |     Element-wise scale: dst = src * factor.
 337 | 
 338 |     Supported dtypes: torch.float16, torch.bfloat16, torch.float32.
 339 | 
 340 |     Parameters
 341 |     ----------
 342 |     src    : CUDA tensor (FP16 / BF16 / FP32)
 343 |     factor : scale factor
 344 |     out    : optional pre-allocated output tensor (same shape/dtype as src)
 345 | 
 346 |     Returns
 347 |     -------
 348 |     Scaled tensor (dst = src * factor).
 349 |     """
 350 |     assert src.is_cuda, "src must be a CUDA tensor"
 351 |     assert src.dtype in (torch.float16, torch.bfloat16, torch.float32), (
 352 |         f"Unsupported dtype {src.dtype}. Supported: float16, bfloat16, float32"
 353 |     )
 354 |     if out is None:
 355 |         out = torch.empty_like(src)
 356 |     else:
 357 |         assert out.shape == src.shape, "out shape must match src"
 358 |         assert out.dtype == src.dtype,  "out dtype must match src"
 359 | 
 360 |     # Encode factor as integer ratio; denom=1000 gives 3 decimal places of precision
 361 |     factor_denom = 1000
 362 |     factor_numer = round(factor * factor_denom)
 363 | 
 364 |     module = _jit_scale_module(src.dtype, factor_numer, factor_denom)
 365 |     module.scale(out, src)
 366 |     return out
 367 | ```
 368 | 
 369 | **Key points:**
 370 | 
 371 | - Use `cache_once` — **not** `functools.lru_cache` (incompatible with `torch.compile`)
 372 | - `load_jit` first arg(s) form the unique build marker; same marker = same cached binary
 373 | - `cuda_wrappers`: `(export_name, kernel_symbol)` — `export_name` is called from Python
 374 | - `make_cpp_args(dtype, ...)` converts `torch.dtype` to C++ type alias:
 375 | 
 376 | | `torch.dtype`      | C++ type   |
 377 | |--------------------|------------|
 378 | | `torch.float16`    | `fp16_t`   |
 379 | | `torch.bfloat16`   | `bf16_t`   |
 380 | | `torch.float32`    | `fp32_t`   |
 381 | 
 382 | ---
 383 | 
 384 | ## Step 3 (optional): Tune JIT build flags
 385 | 
 386 | ```python
 387 | return load_jit(
 388 |     "scale",
 389 |     *args,
 390 |     cuda_files=["elementwise/scale.cuh"],
 391 |     cuda_wrappers=[("scale", f"scale<{args}>")],
 392 |     extra_cuda_cflags=["-O3", "--use_fast_math"],
 393 | )
 394 | ```
 395 | 
 396 | If your kernel requires SM90+, raise a clear Python error before calling `load_jit`:
 397 | 
 398 | ```python
 399 | if torch.cuda.get_device_capability()[0] < 9:
 400 |     raise RuntimeError("This kernel requires SM90 (Hopper) or later")
 401 | ```
 402 | 
 403 | ---
 404 | 
 405 | ## Step 4: Write tests (required)
 406 | 
 407 | Create `python/sglang/jit_kernel/tests/test_scale.py`:
 408 | 
 409 | ```python
 410 | import pytest
 411 | import torch
 412 | from sglang.jit_kernel.scale import scale
 413 | 
 414 | 
 415 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 416 | @pytest.mark.parametrize("size", [1, 127, 128, 1024, 4097])  # cover tail remainder
 417 | @pytest.mark.parametrize("factor", [0.5, 1.0, 2.0, 3.0])
 418 | def test_scale_correctness(dtype, size, factor):
 419 |     src = torch.randn(size, dtype=dtype, device="cuda")
 420 |     out = scale(src, factor)
 421 |     expected = src * factor
 422 | 
 423 |     rtol, atol = (1e-5, 1e-6) if dtype == torch.float32 else (1e-2, 1e-2)
 424 |     torch.testing.assert_close(out, expected, rtol=rtol, atol=atol)
 425 | 
 426 | 
 427 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 428 | def test_scale_out_param(dtype):
 429 |     src = torch.randn(1024, dtype=dtype, device="cuda")
 430 |     out = torch.empty_like(src)
 431 |     result = scale(src, 2.0, out=out)
 432 |     assert result is out
 433 |     torch.testing.assert_close(out, src * 2.0, rtol=1e-2, atol=1e-2)
 434 | 
 435 | 
 436 | def test_scale_cpu_error():
 437 |     src = torch.randn(128, dtype=torch.float16)  # CPU tensor
 438 |     with pytest.raises(AssertionError, match="CUDA"):
 439 |         scale(src, 2.0)
 440 | 
 441 | 
 442 | def test_scale_unsupported_dtype():
 443 |     src = torch.randint(0, 10, (128,), dtype=torch.int32, device="cuda")
 444 |     with pytest.raises(AssertionError, match="Unsupported dtype"):
 445 |         scale(src, 2.0)
 446 | 
 447 | 
 448 | if __name__ == "__main__":
 449 |     pytest.main([__file__, "-v", "-s"])
 450 | ```
 451 | 
 452 | ---
 453 | 
 454 | ## Step 5: Add a benchmark (required)
 455 | 
 456 | Create `python/sglang/jit_kernel/benchmark/bench_scale.py`:
 457 | 
 458 | ```python
 459 | import itertools
 460 | 
 461 | import torch
 462 | import triton
 463 | import triton.testing
 464 | 
 465 | from sglang.jit_kernel.benchmark.utils import (
 466 |     DEFAULT_DEVICE,
 467 |     DEFAULT_DTYPE,
 468 |     get_benchmark_range,
 469 |     run_benchmark,
 470 | )
 471 | from sglang.jit_kernel.scale import scale as jit_scale
 472 | 
 473 | 
 474 | SIZE_LIST = get_benchmark_range(
 475 |     full_range=[2**n for n in range(10, 20)],  # 1K … 512K elements
 476 |     ci_range=[4096, 65536],
 477 | )
 478 | 
 479 | configs = list(itertools.product(SIZE_LIST))
 480 | 
 481 | 
 482 | @triton.testing.perf_report(
 483 |     triton.testing.Benchmark(
 484 |         x_names=["size"],
 485 |         x_vals=configs,
 486 |         line_arg="provider",
 487 |         line_vals=["jit", "torch"],
 488 |         line_names=["SGL JIT Kernel", "PyTorch"],
 489 |         styles=[("blue", "-"), ("red", "--")],
 490 |         ylabel="us",
 491 |         plot_name="scale-performance",
 492 |         args={},
 493 |     )
 494 | )
 495 | def benchmark(size: int, provider: str):
 496 |     src = torch.randn(size, dtype=DEFAULT_DTYPE, device=DEFAULT_DEVICE)
 497 |     factor = 2.0
 498 | 
 499 |     if provider == "jit":
 500 |         fn = lambda: jit_scale(src, factor)
 501 |     else:
 502 |         fn = lambda: src * factor
 503 | 
 504 |     return run_benchmark(fn)
 505 | 
 506 | 
 507 | if __name__ == "__main__":
 508 |     benchmark.run(print_data=True)
 509 | ```
 510 | 
 511 | Run:
 512 | 
 513 | ```bash
 514 | python python/sglang/jit_kernel/benchmark/bench_scale.py
 515 | ```
 516 | 
 517 | ---
 518 | 
 519 | ## Troubleshooting
 520 | 
 521 | - **JIT compilation fails**: ensure the `.cuh` file is under `python/sglang/jit_kernel/csrc/`; reduce template argument combinations
 522 | - **CUDA crash / illegal memory access**: `CUDA_LAUNCH_BLOCKING=1`; `compute-sanitizer --tool memcheck python ...`
 523 | - **Unstable benchmark results**: `run_benchmark` uses CUDA-graph-based timing by default
 524 | 
 525 | ---
 526 | 
 527 | ## References
 528 | 
 529 | - `docs/developer_guide/development_jit_kernel_guide.md`
 530 | - `python/sglang/jit_kernel/utils.py` — `cache_once`, `load_jit`, `make_cpp_args`
 531 | - `python/sglang/jit_kernel/include/sgl_kernel/tensor.h` — `TensorMatcher`, `SymbolicSize/DType/Device`
 532 | - `python/sglang/jit_kernel/include/sgl_kernel/utils.cuh` — type aliases, `LaunchKernel`, `SGL_DEVICE`
 533 | - `python/sglang/jit_kernel/include/sgl_kernel/vec.cuh` — `AlignedVector`
 534 | - `python/sglang/jit_kernel/include/sgl_kernel/tile.cuh` — `tile::Memory`
 535 | - `python/sglang/jit_kernel/include/sgl_kernel/type.cuh` — `dtype_trait`, `packed_t`, `device::cast`
 536 | - `python/sglang/jit_kernel/include/sgl_kernel/math.cuh` — `device::math::`
 537 | - `python/sglang/jit_kernel/include/sgl_kernel/warp.cuh` — `warp::reduce_sum/max`
 538 | - `python/sglang/jit_kernel/include/sgl_kernel/cta.cuh` — `cta::reduce_max`
 539 | - `python/sglang/jit_kernel/include/sgl_kernel/atomic.cuh` — `atomic::max`
 540 | - `python/sglang/jit_kernel/include/sgl_kernel/runtime.cuh` — occupancy / SM count helpers
 541 | - `python/sglang/jit_kernel/csrc/add_constant.cuh` — minimal runnable reference
 542 | - `python/sglang/jit_kernel/csrc/elementwise/rmsnorm.cuh` — real example using `TensorMatcher` + `LaunchKernel` + `tile::Memory`
 543 | - `python/sglang/jit_kernel/csrc/elementwise/qknorm.cuh` — real example using `runtime::get_blocks_per_sm` + persistent kernel pattern
 544 | - `python/sglang/jit_kernel/benchmark/utils.py` — benchmark helpers
 545 | 
 546 | ## Summary of Files Created
 547 | 
 548 | ```
 549 | python/sglang/jit_kernel/csrc/elementwise/scale.cuh   # NEW: CUDA kernel
 550 | python/sglang/jit_kernel/scale.py                     # NEW: Python wrapper
 551 | python/sglang/jit_kernel/tests/test_scale.py          # NEW: Tests
 552 | python/sglang/jit_kernel/benchmark/bench_scale.py     # NEW: Benchmark
 553 | ```
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
  21 | 1. **Heavyweight kernels go to `sgl-kernel`.** If it depends on CUTLASS / FlashInfer / DeepGEMM (or similarly heavy stacks), implement it in `sgl-kernel/`.
  22 | 2. **Lightweight kernels go to `python/sglang/jit_kernel`.** If it is small, has few dependencies, and benefits from rapid iteration, implement it as a JIT kernel instead.
  23 | 
  24 | In addition, every new kernel must ship with:
  25 | 
  26 | - **Tests** (pytest)
  27 | - **A benchmark script** (triton.testing)
  28 | 
  29 | ---
  30 | 
  31 | ## Repository integration map
  32 | 
  33 | You will typically touch these files/areas:
  34 | 
  35 | - Implementation: `sgl-kernel/csrc/elementwise/scale.cu` (pick the right subdirectory)
  36 | - Public declarations: `sgl-kernel/include/sgl_kernel_ops.h`
  37 | - Torch extension registration: `sgl-kernel/csrc/common_extension.cc`
  38 | - Build: `sgl-kernel/CMakeLists.txt` (`set(SOURCES ...)`)
  39 | - Python API: `sgl-kernel/python/sgl_kernel/` and `sgl-kernel/python/sgl_kernel/__init__.py`
  40 | - Tests: `sgl-kernel/tests/test_scale.py`
  41 | - Benchmarks: `sgl-kernel/benchmark/bench_scale.py`
  42 | 
  43 | ---
  44 | 
  45 | ## Step 1: Implement the kernel in `csrc/`
  46 | 
  47 | Pick the right subdirectory:
  48 | 
  49 | - `csrc/elementwise/` — for element-wise ops (our example)
  50 | - `csrc/gemm/`, `csrc/attention/`, `csrc/moe/` — for other categories
  51 | 
  52 | Create `sgl-kernel/csrc/elementwise/scale.cu`:
  53 | 
  54 | ```cpp
  55 | #include <ATen/cuda/CUDAContext.h>
  56 | #include <c10/cuda/CUDAGuard.h>
  57 | #include <torch/all.h>
  58 | 
  59 | #include "utils.h"  // DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16
  60 | 
  61 | // scale_kernel: out[i] = input[i] * factor
  62 | // Supports float, half (__half), __nv_bfloat16 via template T
  63 | template <typename T>
  64 | __global__ void scale_kernel(T* __restrict__ out,
  65 |                               const T* __restrict__ input,
  66 |                               float factor,
  67 |                               int64_t n) {
  68 |   int64_t idx = static_cast<int64_t>(blockIdx.x) * blockDim.x + threadIdx.x;
  69 |   if (idx < n) {
  70 |     out[idx] = static_cast<T>(static_cast<float>(input[idx]) * factor);
  71 |   }
  72 | }
  73 | 
  74 | void scale(at::Tensor& out, const at::Tensor& input, double factor) {
  75 |   TORCH_CHECK(input.is_cuda(),       "input must be a CUDA tensor");
  76 |   TORCH_CHECK(input.is_contiguous(), "input must be contiguous");
  77 |   TORCH_CHECK(out.is_cuda(),         "out must be a CUDA tensor");
  78 |   TORCH_CHECK(out.is_contiguous(),   "out must be contiguous");
  79 |   TORCH_CHECK(out.sizes() == input.sizes(),  "out and input must have the same shape");
  80 |   TORCH_CHECK(out.scalar_type() == input.scalar_type(),
  81 |               "out and input must have the same dtype");
  82 | 
  83 |   const int64_t n = input.numel();
  84 |   const int threads = 256;
  85 |   const int blocks  = (n + threads - 1) / threads;
  86 | 
  87 |   const cudaStream_t stream = at::cuda::getCurrentCUDAStream();
  88 |   const at::cuda::OptionalCUDAGuard device_guard(device_of(input));
  89 | 
  90 |   // Dispatches over float, float16, bfloat16
  91 |   DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16(input.scalar_type(), c_type, [&] {
  92 |     scale_kernel<c_type><<<blocks, threads, 0, stream>>>(
  93 |         static_cast<c_type*>(out.data_ptr()),
  94 |         static_cast<const c_type*>(input.data_ptr()),
  95 |         static_cast<float>(factor),
  96 |         n);
  97 |     cudaError_t status = cudaGetLastError();
  98 |     TORCH_CHECK(status == cudaSuccess,
  99 |                 "scale_kernel launch failed: ", cudaGetErrorString(status));
 100 |     return true;
 101 |   });
 102 | }
 103 | ```
 104 | 
 105 | **Key points:**
 106 | 
 107 | - Use `at::Tensor` (PyTorch tensors), `TORCH_CHECK` for validation, `at::cuda::getCurrentCUDAStream()` for stream
 108 | - `DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16` covers `float`, `half` (FP16), `__nv_bfloat16` (BF16)
 109 | - Add device error checking after every kernel launch
 110 | - If a kernel only works on certain architectures, enforce that with `TORCH_CHECK` and skip logic in tests
 111 | 
 112 | ---
 113 | 
 114 | ## Step 2: Add a C++ declaration in `include/sgl_kernel_ops.h`
 115 | 
 116 | Edit `sgl-kernel/include/sgl_kernel_ops.h`, add to the elementwise section:
 117 | 
 118 | ```cpp
 119 | void scale(at::Tensor& out, const at::Tensor& input, double factor);
 120 | ```
 121 | 
 122 | ---
 123 | 
 124 | ## Step 3: Register the op in `csrc/common_extension.cc`
 125 | 
 126 | Edit `sgl-kernel/csrc/common_extension.cc`, inside `TORCH_LIBRARY_FRAGMENT(sgl_kernel, m)`:
 127 | 
 128 | ```cpp
 129 | // From csrc/elementwise
 130 | m.def("scale(Tensor! out, Tensor input, float factor) -> ()");
 131 | m.impl("scale", torch::kCUDA, &scale);
 132 | ```
 133 | 
 134 | **Key points:**
 135 | 
 136 | - `Tensor!` means in-place / mutable output argument
 137 | - The schema is important for `torch.compile` and for consistent call signatures
 138 | - If your underlying C++ API uses `float` but PyTorch bindings expect `double`, the implicit cast is fine for scalars; use shims if needed for other types
 139 | 
 140 | ---
 141 | 
 142 | ## Step 4: Add the new source file to `CMakeLists.txt`
 143 | 
 144 | Edit `sgl-kernel/CMakeLists.txt`, add to `set(SOURCES ...)`:
 145 | 
 146 | ```cmake
 147 | csrc/elementwise/scale.cu
 148 | ```
 149 | 
 150 | **Key points:**
 151 | 
 152 | - Keep the list **alphabetically sorted** (the file explicitly requires this)
 153 | - If the kernel has arch constraints, reflect that in tests/benchmarks via skip logic
 154 | 
 155 | ---
 156 | 
 157 | ## Step 5: Expose a Python API under `sgl-kernel/python/sgl_kernel/`
 158 | 
 159 | In `sgl-kernel/python/sgl_kernel/__init__.py`, add:
 160 | 
 161 | ```python
 162 | from torch.ops import sgl_kernel as _ops
 163 | 
 164 | def scale(out: torch.Tensor, input: torch.Tensor, factor: float) -> None:
 165 |     """
 166 |     Element-wise scale: out = input * factor (in-place into out).
 167 | 
 168 |     Supported dtypes: torch.float16, torch.bfloat16, torch.float32.
 169 | 
 170 |     Parameters
 171 |     ----------
 172 |     out    : pre-allocated CUDA output tensor (same shape/dtype as input)
 173 |     input  : CUDA input tensor
 174 |     factor : scale factor (float)
 175 |     """
 176 |     _ops.scale(out, input, factor)
 177 | ```
 178 | 
 179 | Or export it from the existing module organisation — follow the pattern already used by similar ops in `__init__.py`.
 180 | 
 181 | ---
 182 | 
 183 | ## Step 6: Write tests (required)
 184 | 
 185 | Create `sgl-kernel/tests/test_scale.py`:
 186 | 
 187 | ```python
 188 | import pytest
 189 | import torch
 190 | import sgl_kernel
 191 | 
 192 | 
 193 | @pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
 194 | @pytest.mark.parametrize("size", [128, 1024, 4096, 65536])
 195 | @pytest.mark.parametrize("factor", [0.5, 1.0, 2.0])
 196 | def test_scale_correctness(dtype, size, factor):
 197 |     input = torch.randn(size, dtype=dtype, device="cuda")
 198 |     out   = torch.empty_like(input)
 199 | 
 200 |     sgl_kernel.scale(out, input, factor)
 201 | 
 202 |     expected = input * factor
 203 |     rtol, atol = (1e-5, 1e-6) if dtype == torch.float32 else (1e-2, 1e-2)
 204 |     torch.testing.assert_close(out, expected, rtol=rtol, atol=atol)
 205 | 
 206 | 
 207 | def test_scale_shape_mismatch():
 208 |     input = torch.randn(128, dtype=torch.float16, device="cuda")
 209 |     out   = torch.empty(256, dtype=torch.float16, device="cuda")
 210 |     with pytest.raises(RuntimeError, match="same shape"):
 211 |         sgl_kernel.scale(out, input, 2.0)
 212 | 
 213 | 
 214 | def test_scale_cpu_input():
 215 |     input = torch.randn(128, dtype=torch.float16)  # CPU
 216 |     out   = torch.empty_like(input)
 217 |     with pytest.raises(RuntimeError, match="CUDA"):
 218 |         sgl_kernel.scale(out, input, 2.0)
 219 | 
 220 | 
 221 | if __name__ == "__main__":
 222 |     pytest.main([__file__, "-q"])
 223 | ```
 224 | 
 225 | Run:
 226 | 
 227 | ```bash
 228 | pytest sgl-kernel/tests/test_scale.py -q
 229 | ```
 230 | 
 231 | ---
 232 | 
 233 | ## Step 7: Add a benchmark (required)
 234 | 
 235 | Create `sgl-kernel/benchmark/bench_scale.py`:
 236 | 
 237 | ```python
 238 | import itertools
 239 | import os
 240 | 
 241 | import torch
 242 | import triton
 243 | import triton.testing
 244 | 
 245 | import sgl_kernel
 246 | 
 247 | IS_CI = (
 248 |     os.getenv("CI", "false").lower() == "true"
 249 |     or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
 250 | )
 251 | 
 252 | dtypes  = [torch.float16] if IS_CI else [torch.float16, torch.bfloat16, torch.float32]
 253 | sizes   = [4096] if IS_CI else [2**n for n in range(10, 20)]  # 1K … 512K
 254 | factors = [2.0]
 255 | 
 256 | configs = list(itertools.product(dtypes, sizes))
 257 | 
 258 | 
 259 | def torch_scale(input: torch.Tensor, factor: float) -> torch.Tensor:
 260 |     return input * factor
 261 | 
 262 | 
 263 | @triton.testing.perf_report(
 264 |     triton.testing.Benchmark(
 265 |         x_names=["dtype", "size"],
 266 |         x_vals=configs,
 267 |         line_arg="provider",
 268 |         line_vals=["sglang", "torch"],
 269 |         line_names=["SGL Kernel", "PyTorch"],
 270 |         styles=[("green", "-"), ("red", "--")],
 271 |         ylabel="µs (median)",
 272 |         plot_name="scale-performance",
 273 |         args={},
 274 |     )
 275 | )
 276 | def benchmark(dtype, size, provider):
 277 |     input  = torch.randn(size, dtype=dtype, device="cuda")
 278 |     out    = torch.empty_like(input)
 279 |     factor = 2.0
 280 | 
 281 |     if provider == "sglang":
 282 |         fn = lambda: sgl_kernel.scale(out, input, factor)
 283 |     else:
 284 |         fn = lambda: torch_scale(input, factor)
 285 | 
 286 |     ms, min_ms, max_ms = triton.testing.do_bench_cudagraph(
 287 |         fn, quantiles=[0.5, 0.2, 0.8]
 288 |     )
 289 |     return 1000 * ms, 1000 * max_ms, 1000 * min_ms
 290 | 
 291 | 
 292 | if __name__ == "__main__":
 293 |     benchmark.run(print_data=True)
 294 | ```
 295 | 
 296 | Run:
 297 | 
 298 | ```bash
 299 | python sgl-kernel/benchmark/bench_scale.py
 300 | ```
 301 | 
 302 | ---
 303 | 
 304 | ## Step 8: Build and validate
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
 320 | Validate:
 321 | 
 322 | ```bash
 323 | pytest sgl-kernel/tests/test_scale.py -q
 324 | python sgl-kernel/benchmark/bench_scale.py
 325 | ```
 326 | 
 327 | ---
 328 | 
 329 | ## Troubleshooting
 330 | 
 331 | - **Async CUDA errors**: `CUDA_LAUNCH_BLOCKING=1`
 332 | - **Memory errors**: `compute-sanitizer --tool memcheck python ...`
 333 | - **Build is too slow / OOM**: reduce `MAX_JOBS` and `SGL_KERNEL_COMPILE_THREADS`
 334 | - **Binary bloat**: use `sgl-kernel/analyze_whl_kernel_sizes.py`
 335 | - **CMake sources list**: if your `.cu` file is missing from `SOURCES`, the symbol will be undefined at link time
 336 | 
 337 | ---
 338 | 
 339 | ## References
 340 | 
 341 | - `sgl-kernel/README.md`
 342 | - `sgl-kernel/include/sgl_kernel_ops.h`
 343 | - `sgl-kernel/csrc/common_extension.cc`
 344 | - `sgl-kernel/CMakeLists.txt`
 345 | - `sgl-kernel/include/utils.h` — `DISPATCH_PYTORCH_DTYPE_TO_CTYPE_FLOAT_FP16` macro and friends
 346 | - `sgl-kernel/csrc/elementwise/activation.cu` — reference for the FP16/BF16/FP32 dispatch pattern
 347 | 
 348 | ## Summary of Files Created/Modified
 349 | 
 350 | ```
 351 | sgl-kernel/csrc/elementwise/scale.cu          # NEW: CUDA kernel + launcher
 352 | sgl-kernel/include/sgl_kernel_ops.h           # MODIFIED: C++ declaration
 353 | sgl-kernel/csrc/common_extension.cc           # MODIFIED: schema + dispatch registration
 354 | sgl-kernel/CMakeLists.txt                     # MODIFIED: add source file (alphabetical)
 355 | sgl-kernel/python/sgl_kernel/__init__.py      # MODIFIED: export Python API
 356 | sgl-kernel/tests/test_scale.py                # NEW: tests
 357 | sgl-kernel/benchmark/bench_scale.py           # NEW: benchmark
 358 | ```
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
   3 | description: Guide for writing SGLang CI/UT tests following project conventions. Covers CustomTestCase, CI registration, server fixtures, model selection, and test placement. Use when creating new tests, adding CI test cases, writing unit tests, or when the user asks to add tests for SGLang features.
   4 | ---
   5 | 
   6 | # Writing SGLang CI / UT Tests
   7 | 
   8 | ## Core Rules
   9 | 
  10 | 1. **Always use `CustomTestCase`** — never raw `unittest.TestCase`
  11 | 2. **Place tests in `test/registered/<category>/`** — only use `test/manual/` for debugging / non-CI tests
  12 | 3. **Reuse server fixtures** — inherit from `DefaultServerBase` or write `setUpClass`/`tearDownClass` with `popen_launch_server`
  13 | 4. **Smallest model for model-agnostic functionality** — use `DEFAULT_SMALL_MODEL_NAME_FOR_TEST` (Llama-3.2-1B-Instruct) for basic features that don't depend on model size
  14 | 5. **8B for general performance** — use `DEFAULT_MODEL_NAME_FOR_TEST` (Llama-3.1-8B-Instruct, single-node) for performance tests that don't involve spec / DP / parallelism
  15 | 6. **Bigger features → discuss case by case** — spec, DP attention, tensor/pipeline parallelism etc. may need multi-GPU suites and specific models
  16 | 
  17 | ---
  18 | 
  19 | ## Test File Template
  20 | 
  21 | ### Functional correctness test (small model)
  22 | 
  23 | ```python
  24 | import unittest
  25 | 
  26 | import requests
  27 | 
  28 | from sglang.srt.utils import kill_process_tree
  29 | from sglang.test.ci.ci_register import register_cuda_ci
  30 | from sglang.test.test_utils import (
  31 |     DEFAULT_SMALL_MODEL_NAME_FOR_TEST,
  32 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
  33 |     DEFAULT_URL_FOR_TEST,
  34 |     CustomTestCase,
  35 |     popen_launch_server,
  36 | )
  37 | 
  38 | register_cuda_ci(est_time=60, suite="stage-b-test-small-1-gpu")
  39 | 
  40 | 
  41 | class TestMyFeature(CustomTestCase):
  42 |     @classmethod
  43 |     def setUpClass(cls):
  44 |         cls.model = DEFAULT_SMALL_MODEL_NAME_FOR_TEST
  45 |         cls.base_url = DEFAULT_URL_FOR_TEST
  46 |         cls.process = popen_launch_server(
  47 |             cls.model,
  48 |             cls.base_url,
  49 |             timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
  50 |             other_args=["--arg1", "value1"],  # feature-specific args
  51 |         )
  52 | 
  53 |     @classmethod
  54 |     def tearDownClass(cls):
  55 |         kill_process_tree(cls.process.pid)
  56 | 
  57 |     def test_basic_functionality(self):
  58 |         response = requests.post(
  59 |             self.base_url + "/generate",
  60 |             json={"text": "Hello", "sampling_params": {"max_new_tokens": 32}},
  61 |         )
  62 |         self.assertEqual(response.status_code, 200)
  63 | 
  64 | 
  65 | if __name__ == "__main__":
  66 |     unittest.main(verbosity=3)
  67 | ```
  68 | 
  69 | ### General performance test (8B model, single node, no spec/DP/parallelism)
  70 | 
  71 | ```python
  72 | import time
  73 | import unittest
  74 | 
  75 | import requests
  76 | 
  77 | from sglang.srt.utils import kill_process_tree
  78 | from sglang.test.ci.ci_register import register_cuda_ci
  79 | from sglang.test.test_utils import (
  80 |     DEFAULT_MODEL_NAME_FOR_TEST,
  81 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
  82 |     DEFAULT_URL_FOR_TEST,
  83 |     CustomTestCase,
  84 |     popen_launch_server,
  85 | )
  86 | 
  87 | register_cuda_ci(est_time=300, suite="stage-b-test-large-1-gpu")
  88 | 
  89 | 
  90 | class TestMyFeaturePerf(CustomTestCase):
  91 |     @classmethod
  92 |     def setUpClass(cls):
  93 |         cls.model = DEFAULT_MODEL_NAME_FOR_TEST
  94 |         cls.base_url = DEFAULT_URL_FOR_TEST
  95 |         cls.process = popen_launch_server(
  96 |             cls.model,
  97 |             cls.base_url,
  98 |             timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
  99 |         )
 100 | 
 101 |     @classmethod
 102 |     def tearDownClass(cls):
 103 |         kill_process_tree(cls.process.pid)
 104 | 
 105 |     def test_latency(self):
 106 |         start = time.perf_counter()
 107 |         response = requests.post(
 108 |             self.base_url + "/generate",
 109 |             json={"text": "Hello", "sampling_params": {"max_new_tokens": 128}},
 110 |         )
 111 |         elapsed = time.perf_counter() - start
 112 |         self.assertEqual(response.status_code, 200)
 113 |         self.assertLess(elapsed, 5.0, "Latency exceeded threshold")
 114 | 
 115 | 
 116 | if __name__ == "__main__":
 117 |     unittest.main(verbosity=3)
 118 | ```
 119 | 
 120 | ---
 121 | 
 122 | ## Server Fixture Reuse
 123 | 
 124 | For tests that only need a standard server, inherit from `DefaultServerBase` and override class attributes:
 125 | 
 126 | ```python
 127 | from sglang.test.server_fixtures.default_fixture import DefaultServerBase
 128 | 
 129 | class TestMyFeature(DefaultServerBase):
 130 |     model = DEFAULT_SMALL_MODEL_NAME_FOR_TEST
 131 |     other_args = ["--enable-my-feature"]
 132 | 
 133 |     def test_something(self):
 134 |         ...
 135 | ```
 136 | 
 137 | Available fixtures in `python/sglang/test/server_fixtures/`:
 138 | 
 139 | | Fixture | Use case |
 140 | |---------|----------|
 141 | | `DefaultServerBase` | Standard single-server tests |
 142 | | `EagleServerBase` | EAGLE speculative decoding |
 143 | | `PDDisaggregationServerBase` | Disaggregated prefill/decode |
 144 | | `MMMUServerBase` | Multimodal VLM tests |
 145 | 
 146 | ---
 147 | 
 148 | ## CI Registration
 149 | 
 150 | Every test file in `test/registered/` **must** call a registration function at module level:
 151 | 
 152 | ```python
 153 | from sglang.test.ci.ci_register import register_cuda_ci, register_amd_ci
 154 | 
 155 | register_cuda_ci(est_time=60, suite="stage-b-test-small-1-gpu")
 156 | register_amd_ci(est_time=60, suite="stage-b-test-small-1-gpu-amd")  # optional
 157 | ```
 158 | 
 159 | Parameters:
 160 | - `est_time`: estimated runtime in seconds (used for CI partitioning)
 161 | - `suite`: which CI suite to run in (see below)
 162 | - `nightly=True`: for nightly-only tests (default `False` = per-commit)
 163 | - `disabled="reason"`: temporarily disable with explanation
 164 | 
 165 | ### Suite selection guide
 166 | 
 167 | **Default cases (1 GPU):**
 168 | 
 169 | | Scenario | Model | Suite |
 170 | |----------|-------|-------|
 171 | | Model-agnostic basic functionality | 1B (smallest) | `stage-b-test-small-1-gpu` |
 172 | | General performance (no spec/DP/parallelism) | 8B | `stage-b-test-large-1-gpu` |
 173 | 
 174 | **Bigger features (case by case):**
 175 | 
 176 | | Scenario | Suite |
 177 | |----------|-------|
 178 | | 2 GPU (e.g. TP=2) | `stage-b-test-large-2-gpu` |
 179 | | 4 GPU (H100) | `stage-c-test-4-gpu-h100` |
 180 | | 8 GPU (H200) | `stage-c-test-8-gpu-h200` |
 181 | | Nightly, 1 GPU | `nightly-1-gpu` |
 182 | | Nightly, 8 GPU | `nightly-8-gpu` |
 183 | 
 184 | For spec, DP attention, parallelism, disaggregation, etc., discuss with the team to determine the appropriate suite and GPU configuration.
 185 | 
 186 | ---
 187 | 
 188 | ## Model Constants
 189 | 
 190 | All defined in `python/sglang/test/test_utils.py`:
 191 | 
 192 | | Constant | Model | When to use |
 193 | |----------|-------|-------------|
 194 | | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST` | Llama-3.2-1B-Instruct | Model-agnostic basic functionality |
 195 | | `DEFAULT_SMALL_MODEL_NAME_FOR_TEST_BASE` | Llama-3.2-1B | Base (non-instruct) model tests |
 196 | | `DEFAULT_MODEL_NAME_FOR_TEST` | Llama-3.1-8B-Instruct | General performance (single node) |
 197 | | `DEFAULT_MOE_MODEL_NAME_FOR_TEST` | Mixtral-8x7B-Instruct | MoE-specific tests |
 198 | | `DEFAULT_SMALL_EMBEDDING_MODEL_NAME_FOR_TEST` | — | Embedding tests |
 199 | | `DEFAULT_SMALL_VLM_MODEL_NAME_FOR_TEST` | — | Vision-language tests |
 200 | 
 201 | ---
 202 | 
 203 | ## Test Placement
 204 | 
 205 | ```
 206 | test/
 207 | ├── registered/          # CI tests (auto-discovered by run_suite.py)
 208 | │   ├── sampling/        # test_penalty.py, test_sampling_params.py ...
 209 | │   ├── sessions/        # test_session_control.py ...
 210 | │   ├── openai_server/   # basic/, features/, validation/ ...
 211 | │   ├── spec/            # eagle/, utils/ ...
 212 | │   ├── models/          # model-specific accuracy tests
 213 | │   ├── perf/            # performance benchmarks
 214 | │   └── <category>/      # create new category if needed
 215 | ├── manual/              # Non-CI: debugging, one-off, manual verification
 216 | └── run_suite.py         # CI runner (scans registered/ only)
 217 | ```
 218 | 
 219 | **Decision rule**: if the test should run in CI → `registered/`. If it's for local debugging or requires special hardware not in CI → `manual/`.
 220 | 
 221 | ---
 222 | 
 223 | ## Key Utilities
 224 | 
 225 | ```python
 226 | from sglang.test.test_utils import (
 227 |     CustomTestCase,              # base class with retry logic
 228 |     popen_launch_server,         # launch server subprocess
 229 |     DEFAULT_URL_FOR_TEST,        # auto-configured base URL
 230 |     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,  # 600s default
 231 |     run_bench_serving,           # benchmark helper (launch + bench)
 232 | )
 233 | from sglang.srt.utils import kill_process_tree  # cleanup server
 234 | ```
 235 | 
 236 | ---
 237 | 
 238 | ## Checklist
 239 | 
 240 | Before submitting a test:
 241 | 
 242 | - [ ] Inherits from `CustomTestCase` (not `unittest.TestCase`)
 243 | - [ ] Has `register_*_ci(...)` call at module level
 244 | - [ ] Placed in `test/registered/<category>/`
 245 | - [ ] Model selection: smallest for model-agnostic features, 8B for general perf, case-by-case for other complex features
 246 | - [ ] `setUpClass` launches server, `tearDownClass` kills it
 247 | - [ ] Has `if __name__ == "__main__": unittest.main(verbosity=3)`
 248 | - [ ] `est_time` is reasonable (measure locally)
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
  25 | - [2026/01] 🔥 SGLang Diffusion accelerates video and image generation ([blog](https://lmsys.org/blog/2026-01-16-sglang-diffusion/)).
  26 | - [2025/12] SGLang provides day-0 support for latest open models ([MiMo-V2-Flash](https://lmsys.org/blog/2025-12-16-mimo-v2-flash/), [Nemotron 3 Nano](https://lmsys.org/blog/2025-12-15-run-nvidia-nemotron-3-nano/), [Mistral Large 3](https://github.com/sgl-project/sglang/pull/14213), [LLaDA 2.0 Diffusion LLM](https://lmsys.org/blog/2025-12-19-diffusion-llm/), [MiniMax M2](https://lmsys.org/blog/2025-11-04-miminmax-m2/)).
  27 | - [2025/10] 🔥 SGLang now runs natively on TPU with the SGLang-Jax backend ([blog](https://lmsys.org/blog/2025-10-29-sglang-jax/)).
  28 | - [2025/09] Deploying DeepSeek on GB200 NVL72 with PD and Large Scale EP (Part II): 3.8x Prefill, 4.8x Decode Throughput ([blog](https://lmsys.org/blog/2025-09-25-gb200-part-2/)).
  29 | - [2025/09] SGLang Day 0 Support for DeepSeek-V3.2 with Sparse Attention ([blog](https://lmsys.org/blog/2025-09-29-deepseek-V32/)).
  30 | - [2025/08] SGLang x AMD SF Meetup on 8/22: Hands-on GPU workshop, tech talks by AMD/xAI/SGLang, and networking ([Roadmap](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_sglang_roadmap.pdf), [Large-scale EP](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_sglang_ep.pdf), [Highlights](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_highlights.pdf), [AITER/MoRI](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_aiter_mori.pdf), [Wave](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/amd_meetup_wave.pdf)).
  31 | 
  32 | <details>
  33 | <summary>More</summary>
  34 | 
  35 | - [2025/11] SGLang Diffusion accelerates video and image generation ([blog](https://lmsys.org/blog/2025-11-07-sglang-diffusion/)).
  36 | - [2025/10] PyTorch Conference 2025 SGLang Talk ([slide](https://github.com/sgl-project/sgl-learning-materials/blob/main/slides/sglang_pytorch_2025.pdf)).
  37 | - [2025/10] SGLang x Nvidia SF Meetup on 10/2 ([recap](https://x.com/lmsysorg/status/1975339501934510231)).
  38 | - [2025/08] SGLang provides day-0 support for OpenAI gpt-oss model ([instructions](https://github.com/sgl-project/sglang/issues/8833))
  39 | - [2025/06] SGLang, the high-performance serving infrastructure powering trillions of tokens daily, has been awarded the third batch of the Open Source AI Grant by a16z ([a16z blog](https://a16z.com/advancing-open-source-ai-through-benchmarks-and-bold-experimentation/)).
  40 | - [2025/05] Deploying DeepSeek with PD Disaggregation and Large-scale Expert Parallelism on 96 H100 GPUs ([blog](https://lmsys.org/blog/2025-05-05-large-scale-ep/)).
  41 | - [2025/06] Deploying DeepSeek on GB200 NVL72 with PD and Large Scale EP (Part I): 2.7x Higher Decoding Throughput ([blog](https://lmsys.org/blog/2025-06-16-gb200-part-1/)).
  42 | - [2025/03] Supercharge DeepSeek-R1 Inference on AMD Instinct MI300X ([AMD blog](https://rocm.blogs.amd.com/artificial-intelligence/DeepSeekR1-Part2/README.html))
  43 | - [2025/03] SGLang Joins PyTorch Ecosystem: Efficient LLM Serving Engine ([PyTorch blog](https://pytorch.org/blog/sglang-joins-pytorch/))
  44 | - [2025/02] Unlock DeepSeek-R1 Inference Performance on AMD Instinct™ MI300X GPU ([AMD blog](https://rocm.blogs.amd.com/artificial-intelligence/DeepSeekR1_Perf/README.html))
  45 | - [2025/01] SGLang provides day one support for DeepSeek V3/R1 models on NVIDIA and AMD GPUs with DeepSeek-specific optimizations. ([instructions](https://github.com/sgl-project/sglang/tree/main/benchmark/deepseek_v3), [AMD blog](https://www.amd.com/en/developer/resources/technical-articles/amd-instinct-gpus-power-deepseek-v3-revolutionizing-ai-development-with-sglang.html), [10+ other companies](https://x.com/lmsysorg/status/1887262321636221412))
  46 | - [2024/12] v0.4 Release: Zero-Overhead Batch Scheduler, Cache-Aware Load Balancer, Faster Structured Outputs ([blog](https://lmsys.org/blog/2024-12-04-sglang-v0-4/)).
  47 | - [2024/10] The First SGLang Online Meetup ([slides](https://github.com/sgl-project/sgl-learning-materials?tab=readme-ov-file#the-first-sglang-online-meetup)).
  48 | - [2024/09] v0.3 Release: 7x Faster DeepSeek MLA, 1.5x Faster torch.compile, Multi-Image/Video LLaVA-OneVision ([blog](https://lmsys.org/blog/2024-09-04-sglang-v0-3/)).
  49 | - [2024/07] v0.2 Release: Faster Llama3 Serving with SGLang Runtime (vs. TensorRT-LLM, vLLM) ([blog](https://lmsys.org/blog/2024-07-25-sglang-llama3/)).
  50 | - [2024/02] SGLang enables **3x faster JSON decoding** with compressed finite state machine ([blog](https://lmsys.org/blog/2024-02-05-compressed-fsm/)).
  51 | - [2024/01] SGLang provides up to **5x faster inference** with RadixAttention ([blog](https://lmsys.org/blog/2024-01-17-sglang/)).
  52 | - [2024/01] SGLang powers the serving of the official **LLaVA v1.6** release demo ([usage](https://github.com/haotian-liu/LLaVA?tab=readme-ov-file#demo)).
  53 | 
  54 | </details>
  55 | 
  56 | ## About
  57 | SGLang is a high-performance serving framework for large language models and multimodal models.
  58 | It is designed to deliver low-latency and high-throughput inference across a wide range of setups, from a single GPU to large distributed clusters.
  59 | Its core features include:
  60 | 
  61 | - **Fast Runtime**: Provides efficient serving with RadixAttention for prefix caching, a zero-overhead CPU scheduler, prefill-decode disaggregation, speculative decoding, continuous batching, paged attention, tensor/pipeline/expert/data parallelism, structured outputs, chunked prefill, quantization (FP4/FP8/INT4/AWQ/GPTQ), and multi-LoRA batching.
  62 | - **Broad Model Support**: Supports a wide range of language models (Llama, Qwen, DeepSeek, Kimi, GLM, GPT, Gemma, Mistral, etc.), embedding models (e5-mistral, gte, mcdse), reward models (Skywork), and diffusion models (WAN, Qwen-Image), with easy extensibility for adding new models. Compatible with most Hugging Face models and OpenAI APIs.
  63 | - **Extensive Hardware Support**: Runs on NVIDIA GPUs (GB200/B300/H100/A100/Spark), AMD GPUs (MI355/MI300), Intel Xeon CPUs, Google TPUs, Ascend NPUs, and more.
  64 | - **Active Community**: SGLang is open-source and supported by a vibrant community with widespread industry adoption, powering over 400,000 GPUs worldwide.
  65 | - **RL & Post-Training Backbone**: SGLang is a proven rollout backend across the world, with native RL integrations and adoption by well-known post-training frameworks such as [**AReaL**](https://github.com/inclusionAI/AReaL), [**Miles**](https://github.com/radixark/miles), [**slime**](https://github.com/THUDM/slime), [**Tunix**](https://github.com/google/tunix), [**verl**](https://github.com/volcengine/verl) and more.
  66 | 
  67 | ## Getting Started
  68 | - [Install SGLang](https://docs.sglang.io/get_started/install.html)
  69 | - [Quick Start](https://docs.sglang.io/basic_usage/send_request.html)
  70 | - [Backend Tutorial](https://docs.sglang.io/basic_usage/openai_api_completions.html)
  71 | - [Frontend Tutorial](https://docs.sglang.io/references/frontend/frontend_tutorial.html)
  72 | - [Contribution Guide](https://docs.sglang.io/developer_guide/contribution_guide.html)
  73 | 
  74 | ## Benchmark and Performance
  75 | Learn more in the release blogs: [v0.2 blog](https://lmsys.org/blog/2024-07-25-sglang-llama3/), [v0.3 blog](https://lmsys.org/blog/2024-09-04-sglang-v0-3/), [v0.4 blog](https://lmsys.org/blog/2024-12-04-sglang-v0-4/), [Large-scale expert parallelism](https://lmsys.org/blog/2025-05-05-large-scale-ep/), [GB200 rack-scale parallelism](https://lmsys.org/blog/2025-09-25-gb200-part-2/).
  76 | 
  77 | ## Adoption and Sponsorship
  78 | SGLang has been deployed at large scale, generating trillions of tokens in production each day. It is trusted and adopted by a wide range of leading enterprises and institutions, including xAI, AMD, NVIDIA, Intel, LinkedIn, Cursor, Oracle Cloud, Google Cloud, Microsoft Azure, AWS, Atlas Cloud, Voltage Park, Nebius, DataCrunch, Novita, InnoMatrix, MIT, UCLA, the University of Washington, Stanford, UC Berkeley, Tsinghua University, Jam & Tea Studios, Baseten, and other major technology organizations across North America and Asia.
  79 | As an open-source LLM inference engine, SGLang has become the de facto industry standard, with deployments running on over 400,000 GPUs worldwide.
  80 | SGLang is currently hosted under the non-profit open-source organization [LMSYS](https://lmsys.org/about/).
  81 | 
  82 | <img src="https://raw.githubusercontent.com/sgl-project/sgl-learning-materials/refs/heads/main/slides/adoption.png" alt="logo" width="800" margin="10px"></img>
  83 | 
  84 | ## Contact Us
  85 | For enterprises interested in adopting or deploying SGLang at scale, including technical consulting, sponsorship opportunities, or partnership inquiries, please contact us at sglang@lmsys.org
  86 | 
  87 | ## Acknowledgment
  88 | We learned the design and reused code from the following projects: [Guidance](https://github.com/guidance-ai/guidance), [vLLM](https://github.com/vllm-project/vllm), [LightLLM](https://github.com/ModelTC/lightllm), [FlashInfer](https://github.com/flashinfer-ai/flashinfer), [Outlines](https://github.com/outlines-dev/outlines), and [LMQL](https://github.com/eth-sri/lmql).
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
  99 | ## Perf Measurement
 100 | 
 101 | Look for `Pixel data generated successfully in xxxx seconds` in console output. With warmup enabled, use the line containing `warmup excluded` for accurate timing.
 102 | 
 103 | ## Env Vars
 104 | 
 105 | Defined in `envs.py` (300+ vars). Key ones:
 106 | - `SGLANG_DIFFUSION_ATTENTION_BACKEND` — attention backend override
 107 | - `SGLANG_CACHE_DIT_ENABLED` — enable Cache-DiT acceleration
 108 | - `SGLANG_CLOUD_STORAGE_TYPE` — cloud output storage (s3, etc.)
```


---
## python/sglang/multimodal_gen/.claude/skills/diffusion-kernel/SKILL.md

```
   1 | ---
   2 | name: diffusion-kernel
   3 | description: Index for SGLang Diffusion kernel development skills.
   4 | ---
   5 | 
   6 | # Diffusion Kernel Skills
   7 | 
   8 | ## Directory Layout
   9 | 
  10 | ```
  11 | python/sglang/multimodal_gen/.claude/skills/diffusion-kernel/
  12 | ├── SKILL.md
  13 | ├── add-triton-kernel.md
  14 | ├── diffusion-benchmark-and-profile.md
  15 | ├── nsight-profiler.md
  16 | └── use-efficient-diffusion-kernels.md
  17 | ```
  18 | 
  19 | ## Index
  20 | 
  21 | - [add-triton-kernel.md](./add-triton-kernel.md)
  22 | 
  23 |   Step-by-step guide for adding a new Triton kernel to SGLang Diffusion's `jit_kernel` module, including authoring, autotune, `torch.compile` compatibility, integration, and tests.
  24 | 
  25 | - [use-efficient-diffusion-kernels.md](./use-efficient-diffusion-kernels.md)
  26 | 
  27 |   Practical guidance for using SGLang Diffusion fused kernels and fast CUDA paths, including constraints, fallbacks, and where the fused ops are wired into the runtime.
  28 | 
  29 | - [diffusion-benchmark-and-profile.md](./diffusion-benchmark-and-profile.md)
  30 | 
  31 |   End-to-end benchmarking and profiling guide for SGLang Diffusion models, including denoise latency measurement, per-layer breakdown, and regression tracking.
  32 | 
  33 | - [nsight-profiler.md](./nsight-profiler.md)
  34 | 
  35 |   Advanced profiling skill for NVIDIA Nsight Systems / Nsight Compute: collecting traces, reading reports, and interpreting kernel-level performance metrics.
```


---
## python/sglang/multimodal_gen/.claude/skills/diffusion-perf/SKILL.md

```
   1 | ---
   2 | name: diffusion-perf
   3 | description: Measure and compare sglang-diffusion performance. Use when benchmarking a model, comparing before/after performance, or generating a perf report for a PR.
   4 | user-invocable: true
   5 | allowed-tools: Bash, Read
   6 | argument-hint: <model-path> [--prompt "..."] [--baseline baseline.json]
   7 | ---
   8 | 
   9 | # Diffusion Performance Measurement
  10 | 
  11 | Measure sglang-diffusion e2e latency via `--perf-dump-path`, then extract or compare results from the JSON dump.
  12 | 
  13 | ## JSON dump structure
  14 | 
  15 | `--perf-dump-path` writes a JSON file with:
  16 | 
  17 | ```json
  18 | {
  19 |   "total_duration_ms": 14959.11,
  20 |   "steps": [
  21 |     {"name": "TextEncodingStage", "duration_ms": 611.83},
  22 |     {"name": "DenoisingStage", "duration_ms": 14289.46}
  23 |   ],
  24 |   "denoise_steps_ms": [
  25 |     {"step": 0, "duration_ms": 240.5},
  26 |     {"step": 1, "duration_ms": 279.1}
  27 |   ],
  28 |   "commit_hash": "abc123",
  29 |   "timestamp": "...",
  30 |   "memory_checkpoints": {}
  31 | }
  32 | ```
  33 | 
  34 | Key fields:
  35 | - `total_duration_ms` — e2e walltime (warmup excluded when `--warmup` is used)
  36 | - `steps` — per-stage breakdown
  37 | - `denoise_steps_ms` — per denoising step timing
  38 | 
  39 | ## Workflow
  40 | 
  41 | ### 1. Single measurement
  42 | 
  43 | ```bash
  44 | sglang generate --model-path $MODEL --prompt "$PROMPT" --warmup --perf-dump-path result.json
  45 | ```
  46 | 
  47 | Then read `total_duration_ms` from `result.json`.
  48 | 
  49 | ### 2. Before/after comparison
  50 | 
  51 | ```bash
  52 | # Baseline (on main branch or before changes)
  53 | sglang generate --model-path $MODEL --prompt "$PROMPT" --warmup --perf-dump-path baseline.json
  54 | 
  55 | # New (after changes)
  56 | sglang generate --model-path $MODEL --prompt "$PROMPT" --warmup --perf-dump-path new.json
  57 | 
  58 | # Compare — outputs a Markdown table suitable for PR descriptions
  59 | python python/sglang/multimodal_gen/benchmarks/compare_perf.py baseline.json new.json
  60 | ```
  61 | 
  62 | ### 3. Extracting a single number
  63 | 
  64 | To get e2e latency in seconds from a dump:
  65 | 
  66 | ```bash
  67 | python3 -c "import json; print(f\"{json.load(open('result.json'))['total_duration_ms']/1000:.2f}\")"
  68 | ```
  69 | 
  70 | ## Arguments
  71 | 
  72 | If `$ARGUMENTS` is provided, parse it as:
  73 | - First positional arg → `--model-path`
  74 | - `--prompt "..."` → generation prompt (default: `"A curious raccoon"`)
  75 | - `--baseline <file>` → if given, run comparison against this baseline file
  76 | 
  77 | ## Notes
  78 | 
  79 | - Always use `--warmup` for accurate timing (excludes CUDA warmup from measurement).
  80 | - Keep `--prompt` and all server/sampling args identical between baseline and new runs.
  81 | - For PR descriptions, paste the output of `compare_perf.py` directly.
```
