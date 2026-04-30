#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flashinfer

# Idempotency guard
if grep -qF "- **Destination passing style**: Output tensor(s) are passed as optional paramet" ".claude/skills/add-cuda-kernel/skill.md" && grep -qF "--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16" ".claude/skills/benchmark-kernel/skill.md" && grep -qF "**Solution**: FlashInfer's `@flashinfer_api` decorator logs inputs BEFORE execut" ".claude/skills/debug-cuda-crash/skill.md" && grep -qF "> Because practical engineering involves the accumulated experience of trial and" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-cuda-kernel/skill.md b/.claude/skills/add-cuda-kernel/skill.md
@@ -0,0 +1,750 @@
+# Tutorial: Adding a New Kernel to FlashInfer
+
+This tutorial walks through adding a simple element-wise scale operation to FlashInfer. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.
+
+## Goal
+
+Add a new operation that scales each element of a tensor by a scalar factor:
+
+- Input: tensor `x` and scalar `factor`
+- Output: `x * factor` (element-wise)
+- Support multiple dtypes (FP16, BF16, FP32)
+
+## Step 1: Define CUDA Kernel in `include/`
+
+Create `include/flashinfer/scale.cuh`:
+
+```cpp
+#pragma once
+#include <cuda_runtime.h>
+#include <cuda_fp16.h>
+#include <cuda_bf16.h>
+
+namespace flashinfer {
+
+/*!
+ * \brief Element-wise scale kernel
+ * \tparam T Data type (half, __nv_bfloat16, float)
+ * \param input Input tensor
+ * \param output Output tensor
+ * \param factor Scale factor
+ * \param n Number of elements
+ */
+template <typename T>
+__global__ void ScaleKernel(const T* input, T* output, T factor, int n) {
+  int idx = blockIdx.x * blockDim.x + threadIdx.x;
+  if (idx < n) {
+    output[idx] = input[idx] * factor;
+  }
+}
+
+/*!
+ * \brief Launch scale kernel
+ * \tparam T Data type
+ * \param input Input pointer
+ * \param output Output pointer
+ * \param factor Scale factor
+ * \param n Number of elements
+ * \param stream CUDA stream
+ */
+template <typename T>
+cudaError_t ScaleLauncher(const T* input, T* output, T factor, int n,
+                          cudaStream_t stream = nullptr) {
+  const int threads = 256;
+  const int blocks = (n + threads - 1) / threads;
+
+  ScaleKernel<T><<<blocks, threads, 0, stream>>>(input, output, factor, n);
+
+  return cudaGetLastError();
+}
+
+}  // namespace flashinfer
+```
+
+**Key points:**
+
+- Framework-agnostic (no Torch headers)
+- Uses raw pointers
+- Template-based for dtype flexibility
+- Only includes what's needed (cuda_runtime, cuda_fp16, cuda_bf16)
+
+## Step 2: Create Launcher in `csrc/`
+
+Create `csrc/scale.cu`:
+
+```cpp
+#include "flashinfer/scale.cuh"
+
+using namespace flashinfer;
+
+void scale_launcher(TensorView input, TensorView output,
+                    float factor) {
+  CHECK_INPUT(input);
+  CHECK_INPUT(output);
+  TVM_FFI_ICHECK_EQ(input.dtype(), output.dtype());
+  int n = input.numel();
+  auto stream = get_stream(input.device());
+
+  DISPATCH_DLPACK_DTYPE_TO_CTYPE_FP32_FP16(input.dtype(), DType, [&] {
+    cudaError_t status = ScaleLauncher<DType>(
+      input.data_ptr<DType>(),
+      output.data_ptr<DType>(),
+      static_cast<DType>(factor),
+      n,
+      stream
+    );
+    TVM_FFI_ICHECK(status == cudaSuccess)
+        << "Failed to run ScaleLauncher: " << cudaGetErrorString(status);
+    return true;
+  });
+}
+```
+
+**Key points:**
+
+- Includes TVM FFI utils headers `tvm_ffi_utils.h` (only allowed in `csrc/`)
+- Uses `tvm::ffi::TensorView` as input and output tensor types
+- Uses macros defined in `tvm_ffi_utils.h` to check the input and output if both on CUDA device, both contiguous, and share the same data type
+- Gets CUDA stream by TVM FFI, and prepare all scalar inputs for kernel function
+- Dispatches on dtype with macros defined in `tvm_ffi_utils.h`, or adds new one if not covered
+- Converts tvm::ffi::TensorView to raw pointers
+- Handles the result status of kernel by `TVM_FFI_ICHECK`
+- Add descriptive error messages with `<<` operator
+- **Use TVM-FFI exceptions**: `TVM_FFI_THROW(ErrorType) << "message"` for custom error checking
+
+**TVM-FFI Error Handling:**
+
+- `TVM_FFI_THROW(ValueError) << "message"` - Throw ValueError with custom message
+- `TVM_FFI_THROW(TypeError) << "message"` - Throw TypeError
+- Use `<<` to chain multiple values in the error message
+- Errors are properly propagated back to Python
+
+**When to use `TVM_FFI_THROW` vs `TVM_FFI_LOG_AND_THROW`:**
+
+- **`TVM_FFI_THROW`**: Use for normal runtime error handling. This is the standard way to report errors that will be caught and propagated to Python.
+
+- **`TVM_FFI_LOG_AND_THROW`**: Use only in cases where:
+  1. The function may be called during object construction time (e.g., validation in constructors or setup methods)
+  2. The exception may not be caught properly (e.g., during module initialization)
+  3. The error condition almost never fails in practice (e.g., internal errors, unsupported dtype combinations in dispatch macros)
+
+  This variant logs the error message before throwing, ensuring visibility even if the exception doesn't propagate correctly.
+
+**Example from fused_moe (see `csrc/trtllm_fused_moe_kernel_launcher.cu`):**
+```cpp
+// In a setup/validation function that may be called during construction
+void check_weights_shape(std::string which_weights) const {
+  if (which_weights != "gemm1" && which_weights != "gemm2") {
+    // Internal error that should never happen - use LOG_AND_THROW
+    TVM_FFI_LOG_AND_THROW(InternalError) << "Internal error: which_weights = " << which_weights;
+  }
+  // ...
+  if (weight_layout is unsupported) {
+    // Unsupported config during setup - use LOG_AND_THROW
+    TVM_FFI_LOG_AND_THROW(NotImplementedError)
+        << "Unsupported weight_layout: " << (int)weight_layout;
+  }
+}
+
+// In a normal runtime function
+void scale_run(TensorView input, TensorView output, double factor) {
+  if (!input_tensor.is_cuda()) {
+    // Normal validation error - use TVM_FFI_THROW
+    TVM_FFI_THROW(ValueError) << "Input must be a CUDA tensor";
+  }
+}
+```
+
+## Step 3: Create TVM-FFI Binding in `csrc/`
+
+Create `csrc/scale_jit_binding.cu`:
+
+```cpp
+#include "scale.cu"
+#include "tvm_ffi_utils.h"
+
+// Forward declaration
+void scale_launcher(TensorView input, TensorView output, float factor);
+
+// Export to TVM-FFI
+TVM_FFI_DLL_EXPORT_TYPED_FUNC(run, scale_launcher);
+```
+
+**Key points:**
+
+- Forward declare the launcher function first
+- Export using `TVM_FFI_DLL_EXPORT_TYPED_FUNC(name, function)`
+
+## Step 4: Create JIT Generator (No Jinja for Simple Case)
+
+Create `flashinfer/jit/scale.py`:
+
+```python
+import os
+import shutil
+from pathlib import Path
+
+from . import JitSpec, gen_jit_spec
+from . import env as jit_env
+from .core import write_if_different
+
+
+def get_scale_uri(dtype_in: str, dtype_out: str) -> str:
+    """Generate unique identifier for scale module."""
+    return f"scale_dtype_in_{dtype_in}_dtype_out_{dtype_out}"
+
+
+def gen_scale_module(dtype_in, dtype_out):
+    """
+    Generate JIT module for scale operation.
+
+    Note: This is a simple example without Jinja templating.
+    The dtype dispatch is handled at runtime in the C++ code.
+    """
+    # Compute URI
+    uri = get_scale_uri(dtype_in, dtype_out)
+
+    # Create generation directory
+    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
+    os.makedirs(gen_directory, exist_ok=True)
+
+    # Copy source files (no Jinja needed for this simple case)
+    sources = []
+    for fname in ["scale.cu", "scale_jit_binding.cu"]:
+        src_path = jit_env.FLASHINFER_CSRC_DIR / fname
+        dest_path = gen_directory / fname
+        shutil.copy(src_path, dest_path)
+        sources.append(dest_path)
+
+    # Return JitSpec
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=[],
+    )
+```
+
+**Key points:**
+
+- No Jinja template needed for simple operations
+- Just copy source files to generation directory
+- URI uniquely identifies the module configuration
+
+### (Optional) Specifying Supported CUDA Architectures
+
+FlashInfer uses `CompilationContext` to manage CUDA architecture targets. This is critical because some kernels only work on specific GPU architectures (e.g., Hopper SM90, Blackwell SM100).
+
+#### How CompilationContext Works
+
+**Automatic Detection** (default):
+```python
+from flashinfer.compilation_context import CompilationContext
+
+ctx = CompilationContext()
+# Automatically detects all GPUs in the system
+# For SM90+, adds 'a' suffix (e.g., 9.0a for Hopper)
+# Result: ctx.TARGET_CUDA_ARCHS = {(9, '0a'), (10, '0a'), ...}
+```
+
+**Manual Override** (via environment variable):
+```bash
+export FLASHINFER_CUDA_ARCH_LIST="8.0 9.0a 10.0a"
+# Now only these architectures will be compiled
+```
+
+#### Specifying Architectures in Your JIT Module
+
+When creating a JIT module, specify which major SM versions are supported:
+
+```python
+from flashinfer.jit.core import gen_jit_spec
+from flashinfer.jit import current_compilation_context
+
+def gen_my_hopper_only_module():
+    """Example: Kernel works on SM90 and later supported architectures."""
+    uri = get_my_uri(...)
+    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
+    # ... copy sources ...
+
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        # Explicitly list supported SM versions - no automatic future compatibility
+        supported_major_versions=[9, 10, 11, 12]  # SM90, SM100, SM110, SM120
+    )
+
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+
+def gen_my_blackwell_only_module():
+    """Example: Kernel only works on SM100 (Blackwell)"""
+    uri = get_my_uri(...)
+    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
+    # ... copy sources ...
+
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        supported_major_versions=[10]  # SM100 only
+    )
+
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+
+def gen_my_universal_module():
+    """Example: Kernel works on all architectures"""
+    uri = get_my_uri(...)
+    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
+    # ... copy sources ...
+
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        supported_major_versions=None  # All available architectures
+    )
+
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+```
+
+**What Happens:**
+- ✅ If user's GPU is SM90 and they call a Hopper-only module → Compiles and runs
+- ❌ If user's GPU is SM80 and they call a Hopper-only module → `RuntimeError: No supported CUDA architectures found for major versions [9, 10, 11, 12]`
+
+#### Real Examples from FlashInfer
+
+```python
+# MLA kernel: Blackwell and newer only
+def gen_mla_module() -> JitSpec:
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        supported_major_versions=[10, 11]  # SM100, SM110
+    )
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+
+# Blackwell FMHA: SM120 only
+def gen_fmhav2_blackwell_module(...):
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        supported_major_versions=[12]  # SM120 only
+    )
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+
+# Standard attention: Hopper and later supported architectures
+def gen_batch_prefill_module(...):
+    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
+        supported_major_versions=[9, 10, 11, 12]  # SM90, SM100, SM110, SM120
+    )
+    return gen_jit_spec(
+        name=uri,
+        sources=sources,
+        extra_cuda_cflags=nvcc_flags,
+    )
+```
+
+#### Common Architecture Specifications
+
+| Supported Versions | Architectures | Use Case |
+|-------------------|---------------|----------|
+| `None` | All available GPUs | Universal kernels (default) |
+| `[9, 10, 11, 12]` | SM90, SM100, SM110, SM120 | Hopper, Blackwell |
+| `[10, 11, 12]` | SM100, SM110, SM120 | Blackwell only |
+| `[12]` | SM120 | Specific architecture only |
+| `[8, 9, 10, 11, 12]` | SM80, SM90, SM100, SM110, SM120 | Ampere, Hopper, Blackwell |
+
+#### Testing with Architecture Requirements
+
+When your kernel has architecture requirements, add skip checks in tests (see Step 6 below):
+
+```python
+import pytest
+import torch
+from flashinfer.utils import is_sm90a_supported
+
+def test_hopper_kernel():
+    if not is_sm90a_supported(torch.device("cuda")):
+        pytest.skip("SM90a is not supported on this GPU")
+
+    # Test code here
+    ...
+```
+
+## Step 5: Create Python API in `flashinfer/`
+
+Create `flashinfer/scale.py`:
+
+```python
+import functools
+import torch
+from typing import Optional
+
+from .jit.scale import gen_scale_module
+from .utils import backend_requirement, supported_compute_capability
+from .api_logging import flashinfer_api
+
+
+@functools.cache
+def get_scale_module(dtype_in, dtype_out):
+    """Get or compile scale module (cached)."""
+    return gen_scale_module(dtype_in, dtype_out).build_and_load()
+
+
+@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
+def _check_scale_problem_size(input: torch.Tensor, factor: float,
+                               out: Optional[torch.Tensor] = None) -> bool:
+    """Validate inputs for scale operation."""
+    # Validate input
+    if not input.is_cuda:
+        raise ValueError("Input must be a CUDA tensor")
+
+    # Validate output if provided
+    if out is not None:
+        if out.shape != input.shape:
+            raise ValueError("Output shape mismatch")
+        if out.dtype != input.dtype:
+            raise ValueError("Output dtype mismatch")
+        if not out.is_cuda:
+            raise ValueError("Output must be a CUDA tensor")
+
+    return True
+
+
+@flashinfer_api
+@backend_requirement(
+    backend_checks={},  # No backend choices for this simple kernel
+    common_check=_check_scale_problem_size,
+)
+def scale(input: torch.Tensor, factor: float,
+          out: Optional[torch.Tensor] = None) -> torch.Tensor:
+    """
+    Element-wise scale operation.
+
+    Parameters
+    ----------
+    input : torch.Tensor
+        Input tensor (CUDA)
+    factor : float
+        Scale factor
+    out : Optional[torch.Tensor]
+        Output tensor (if None, allocate new tensor)
+
+    Returns
+    -------
+    output : torch.Tensor
+        Scaled tensor (input * factor)
+
+    Examples
+    --------
+    >>> import torch
+    >>> import flashinfer
+    >>> x = torch.randn(1024, dtype=torch.float16, device="cuda")
+    >>> y = flashinfer.scale(x, 2.0)
+    >>> torch.allclose(y, x * 2.0)
+    True
+    """
+    # Allocate output if needed
+    if out is None:
+        out = torch.empty_like(input)
+
+    # Get module (compile if first call with this dtype)
+    dtype_str = str(input.dtype).replace("torch.", "")
+    module = get_scale_module(dtype_str, dtype_str)
+
+    # Call TVM-FFI function (exported as "run")
+    module.run(input, out, float(factor))
+
+    return out
+```
+
+**Key points:**
+
+- Uses `@functools.cache` to cache compiled modules
+- Clean Python API with docstring
+- Adding the `@flashinfer_api` decorator enables logging and sets it apart from helper functions
+- **Destination passing style**: Output tensor(s) are passed as optional parameters (`out: Optional[torch.Tensor] = None`). This allows users to provide pre-allocated buffers to avoid allocation overhead in performance-critical paths. Only allocate internally when `out` is `None`.
+- Validates inputs using `@backend_requirement` decorator
+
+### Using `@backend_requirement` and `@supported_compute_capability` Decorators
+
+FlashInfer provides two decorators for enforcing compute capability and backend requirements:
+
+#### `@supported_compute_capability` Decorator
+
+Marks a function with its supported CUDA compute capabilities:
+
+```python
+from flashinfer.utils import supported_compute_capability
+
+@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
+def _my_check_function(input, output):
+    """Supports SM80 (Ampere) through SM120 (Blackwell)."""
+    # Validation logic here
+    return True
+```
+
+#### `@backend_requirement` Decorator
+
+Enforces backend and problem size requirements at runtime. There are three usage patterns:
+
+**Pattern 1: Single Backend (No Backend Choices)**
+
+For kernels with only one implementation (like our scale example):
+
+```python
+from flashinfer.utils import backend_requirement, supported_compute_capability
+
+@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
+def _check_my_kernel(input, output):
+    """Validate inputs. Must return True if valid."""
+    if input.shape[-1] > 256:
+        raise ValueError("Head dimension must be <= 256")
+    return True
+
+@backend_requirement(
+    backend_checks={},  # Empty dict = no backend parameter
+    common_check=_check_my_kernel,
+)
+def my_kernel(input, output):
+    # Kernel implementation
+    pass
+```
+
+**Pattern 2: Multiple Backends**
+
+For kernels with multiple implementation backends (e.g., CUTLASS, cuDNN):
+
+```python
+@supported_compute_capability([80, 86, 89, 90])
+def _cutlass_check(q, k, v, backend):
+    """CUTLASS backend: Ampere through Hopper."""
+    if q.shape[-1] > 256:
+        raise ValueError("CUTLASS: head_dim must be <= 256")
+    return True
+
+@supported_compute_capability([75, 80, 86, 89, 90, 100])
+def _cudnn_check(q, k, v, backend):
+    """cuDNN backend: Turing through Blackwell."""
+    return True
+
+@backend_requirement(
+    backend_checks={
+        "cutlass": _cutlass_check,
+        "cudnn": _cudnn_check,
+    },
+    common_check=None,  # Optional: shared validation for all backends
+)
+def attention(q, k, v, backend="cutlass"):
+    if backend == "cutlass":
+        # CUTLASS implementation
+        pass
+    elif backend == "cudnn":
+        # cuDNN implementation
+        pass
+```
+
+**Pattern 3: Auto Backend Selection**
+
+For kernels that can automatically select the best backend:
+
+```python
+def _heuristic_func(suitable_backends, q, k, v, backend):
+    """Return backends in order of preference."""
+    # Prefer CUTLASS for small head dims, cuDNN for larger
+    if q.shape[-1] <= 128:
+        preferred = ["cutlass", "cudnn"]
+    else:
+        preferred = ["cudnn", "cutlass"]
+    return [b for b in preferred if b in suitable_backends]
+
+@backend_requirement(
+    backend_checks={
+        "cutlass": _cutlass_check,
+        "cudnn": _cudnn_check,
+    },
+    common_check=_common_validation,
+    heuristic_func=_heuristic_func,  # Required when backend="auto" is used
+)
+def attention(q, k, v, backend="auto"):
+    if backend == "auto":
+        # Use the first backend from suitable_auto_backends
+        backend = attention.suitable_auto_backends[0]
+    # ... rest of implementation
+```
+
+#### Features Added by `@backend_requirement`
+
+The decorator adds these methods to the wrapped function:
+
+```python
+# Check if a backend is supported (optionally for a specific CC)
+scale.is_backend_supported("cutlass")           # True/False
+scale.is_backend_supported("cutlass", cc=90)    # True/False for Hopper
+
+# Check if any backend supports this compute capability
+scale.is_compute_capability_supported(90)       # True/False
+
+# Check if a backend exists
+scale.has_backend("cutlass")                    # True/False
+
+# Check if there are multiple backend choices
+scale.has_backend_choices()                     # True/False
+```
+
+#### `skip_check` Keyword Argument
+
+The decorator adds a `skip_check` keyword argument to bypass validation for performance-critical code paths:
+
+```python
+# Normal call with validation
+result = scale(x, 2.0)
+
+# Skip validation for performance (use with caution!)
+result = scale(x, 2.0, skip_check=True)
+```
+
+#### Check Function Requirements
+
+Check functions must:
+1. Accept the same arguments as the decorated function
+2. Return `True` if validation passes
+3. Raise `ValueError` with descriptive message if validation fails
+4. Be decorated with `@supported_compute_capability` to specify supported architectures
+
+## Step 6: Write Tests in `tests/`
+
+Create tests in an appropriate subdirectory (e.g., `tests/elementwise/test_scale.py` or create a new subdir if needed):
+
+```python
+import pytest
+import torch
+
+
+@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
+@pytest.mark.parametrize("size", [128, 1024, 4096])
+def test_scale_correctness(dtype, size):
+    """Test scale operation correctness."""
+    import flashinfer
+
+    # Setup
+    x = torch.randn(size, dtype=dtype, device="cuda")
+    factor = 3.14
+
+    # Run FlashInfer kernel
+    y = flashinfer.scale(x, factor)
+
+    # Reference implementation
+    expected = x * factor
+
+    # Compare
+    if dtype == torch.float32:
+        rtol, atol = 1e-5, 1e-6
+    else:
+        rtol, atol = 1e-3, 1e-3
+
+    torch.testing.assert_close(y, expected, rtol=rtol, atol=atol)
+
+
+@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16])
+def test_scale_inplace(dtype):
+    """Test scale with pre-allocated output."""
+    import flashinfer
+
+    x = torch.randn(1024, dtype=dtype, device="cuda")
+    out = torch.empty_like(x)
+    factor = 2.0
+
+    result = flashinfer.scale(x, factor, out=out)
+
+    # Should return the same tensor
+    assert result is out
+
+    # Check correctness
+    expected = x * factor
+    torch.testing.assert_close(result, expected, rtol=1e-3, atol=1e-3)
+
+
+def test_scale_cpu_error():
+    """Test that CPU tensors raise an error."""
+    import flashinfer
+
+    x = torch.randn(128, dtype=torch.float32)
+
+    with pytest.raises(ValueError, match="CUDA"):
+        flashinfer.scale(x, 2.0)
+```
+
+**Key points:**
+
+- Use `pytest.mark.parametrize` for multiple configurations
+- Compare against reference implementation
+- Set appropriate tolerances for each dtype
+- Test error cases
+
+## Step 7: Register in AOT
+
+Register your kernel in AOT so users with `flashinfer-jit-cache` can skip JIT compilation.
+
+Edit `flashinfer/aot.py`, add to the appropriate section:
+
+```python
+def gen_scale_modules() -> Iterator[JitSpec]:
+    """Generate scale operation modules for AOT compilation."""
+    from .jit.scale import gen_scale_module
+
+    # Pre-compile common dtypes
+    for dtype in ["float16", "bfloat16", "float32"]:
+        yield gen_scale_module(dtype, dtype)
+
+
+# In the main AOT build loop, add:
+# for spec in gen_scale_modules():
+#     spec.build()
+```
+
+**Key points:**
+
+- Pre-compile common configurations
+- Users with `flashinfer-jit-cache` won't need to compile at runtime
+
+## Step 8: Export API
+
+Edit `flashinfer/__init__.py`:
+
+```python
+from .scale import scale as scale
+
+# Or in the existing imports section:
+# from .scale import scale
+```
+
+## Step 9: Run and Test
+
+```bash
+# The kernel compiles automatically on first use
+pytest tests/test_scale.py -v
+
+# Run with different dtypes
+pytest tests/test_scale.py::test_scale_correctness[float16-128] -v
+```
+
+## Summary of Files Created/Modified
+
+```
+include/flashinfer/scale.cuh              # NEW: CUDA kernel definition
+csrc/scale.cu                              # NEW: PyTorch launcher
+csrc/scale_jit_binding.cu                  # NEW: TVM-FFI binding
+flashinfer/jit/scale.py                    # NEW: JIT generator
+flashinfer/scale.py                        # NEW: Python API
+flashinfer/__init__.py                     # MODIFIED: Export API
+flashinfer/aot.py                          # MODIFIED: Register AOT
+tests/test_scale.py                        # NEW: Unit tests
+```
diff --git a/.claude/skills/benchmark-kernel/skill.md b/.claude/skills/benchmark-kernel/skill.md
@@ -0,0 +1,417 @@
+# Tutorial: Benchmarking FlashInfer Kernels
+
+This tutorial shows you how to accurately benchmark FlashInfer kernels.
+
+## Goal
+
+Measure the performance of FlashInfer kernels:
+- Get accurate GPU kernel execution time
+- Compare multiple backends (FlashAttention2/3, cuDNN, CUTLASS, TensorRT-LLM)
+- Generate reproducible benchmark results
+- Save results to CSV for analysis
+
+## Timing Methods
+
+FlashInfer supports two timing methods:
+
+1. **CUPTI (Preferred)**: Hardware-level profiling for most accurate GPU kernel time
+   - Measures pure GPU compute time without host-device overhead
+   - Requires `cupti-python >= 13.0.0` (CUDA 13+)
+
+2. **CUDA Events (Fallback)**: Standard CUDA event timing
+   - Automatically used if CUPTI is not available
+   - Good accuracy, slight overhead from host synchronization
+
+**The framework automatically uses CUPTI if available, otherwise falls back to CUDA events.**
+
+## Installation
+
+### Install CUPTI (Recommended)
+
+For the most accurate benchmarking:
+
+```bash
+pip install -U cupti-python
+```
+
+**Requirements**: CUDA 13+ (CUPTI version 13+)
+
+### Without CUPTI
+
+If you don't install CUPTI, the framework will:
+- Print a warning: `CUPTI is not installed. Falling back to CUDA events.`
+- Automatically use CUDA events for timing
+- Still provide good benchmark results
+
+## Method 1: Using flashinfer_benchmark.py (Recommended)
+
+### Step 1: Choose Your Test Routine
+
+Available routines:
+- **Attention**: `BatchDecodeWithPagedKVCacheWrapper`, `BatchPrefillWithPagedKVCacheWrapper`, `BatchPrefillWithRaggedKVCacheWrapper`, `BatchMLAPagedAttentionWrapper`
+- **GEMM**: `bmm_fp8`, `gemm_fp8_nt_groupwise`, `group_gemm_fp8_nt_groupwise`, `mm_fp4`
+- **MOE**: `trtllm_fp4_block_scale_moe`, `trtllm_fp8_block_scale_moe`, `trtllm_fp8_per_tensor_scale_moe`, `cutlass_fused_moe`
+
+### Step 2: Run a Single Benchmark
+
+Example - Benchmark decode attention:
+
+```bash
+# CUPTI will be used automatically if installed
+python benchmarks/flashinfer_benchmark.py \
+    --routine BatchDecodeWithPagedKVCacheWrapper \
+    --backends fa2 fa2_tc cudnn \
+    --page_size 16 \
+    --batch_size 32 \
+    --s_qo 1 \
+    --s_kv 2048 \
+    --num_qo_heads 32 \
+    --num_kv_heads 8 \
+    --head_dim_qk 128 \
+    --head_dim_vo 128 \
+    --q_dtype bfloat16 \
+    --kv_dtype bfloat16 \
+    --num_iters 30 \
+    --dry_run_iters 5 \
+    --refcheck \
+    -vv
+```
+
+Example - Benchmark FP8 GEMM:
+
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine bmm_fp8 \
+    --backends cudnn cublas cutlass \
+    --batch_size 256 \
+    --m 1 \
+    --n 1024 \
+    --k 7168 \
+    --input_dtype fp8_e4m3 \
+    --mat2_dtype fp8_e4m3 \
+    --out_dtype bfloat16 \
+    --refcheck \
+    -vv \
+    --generate_repro_command
+```
+
+**Timing behavior:**
+- ✅ If CUPTI installed: Uses CUPTI (most accurate)
+- ⚠️ If CUPTI not installed: Automatically falls back to CUDA events with warning
+- 🔧 To force CUDA events: Add `--use_cuda_events` flag
+
+### Step 3: Understand the Output
+
+```
+[INFO] FlashInfer version: 0.6.0
+[VVERBOSE] gpu_name = 'NVIDIA_H100_PCIe'
+[PERF] fa2            :: median time 0.145 ms; std 0.002 ms; achieved tflops 125.3 TFLOPs/sec; achieved tb_per_sec 1.87 TB/sec
+[PERF] fa2_tc         :: median time 0.138 ms; std 0.001 ms; achieved tflops 131.5 TFLOPs/sec; achieved tb_per_sec 1.96 TB/sec
+[PERF] cudnn          :: median time 0.142 ms; std 0.001 ms; achieved tflops 127.8 TFLOPs/sec; achieved tb_per_sec 1.91 TB/sec
+```
+
+**Key metrics:**
+- **median time**: Median kernel execution time (lower is better)
+- **std**: Standard deviation (lower means more consistent)
+- **achieved tflops**: Effective TFLOPS throughput
+- **achieved tb_per_sec**: Memory bandwidth utilization
+
+### Step 4: Run Batch Benchmarks
+
+Create a test list file `my_benchmarks.txt`:
+
+```bash
+--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 32 --s_kv 2048 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128
+--routine BatchDecodeWithPagedKVCacheWrapper --backends fa2 cudnn --page_size 16 --batch_size 64 --s_kv 4096 --num_qo_heads 32 --num_kv_heads 8 --head_dim_qk 128 --head_dim_vo 128
+--routine bmm_fp8 --backends cudnn cutlass --batch_size 256 --m 1 --n 1024 --k 7168 --input_dtype fp8_e4m3 --mat2_dtype fp8_e4m3 --out_dtype bfloat16
+```
+
+Run all tests:
+
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --testlist my_benchmarks.txt \
+    --output_path results.csv \
+    --generate_repro_command \
+    --refcheck
+```
+
+Results are saved to `results.csv` with all metrics and reproducer commands.
+
+### Step 5: Common Flags
+
+| Flag | Description | Default |
+|------|-------------|---------|
+| `--num_iters` | Measurement iterations | 30 |
+| `--dry_run_iters` | Warmup iterations | 5 |
+| `--refcheck` | Verify output correctness | False |
+| `--allow_output_mismatch` | Continue on mismatch | False |
+| `--use_cuda_events` | Force CUDA events (skip CUPTI) | False |
+| `--no_cuda_graph` | Disable CUDA graph | False |
+| `-vv` | Very verbose output | - |
+| `--generate_repro_command` | Print reproducer command | False |
+| `--case_tag` | Tag for CSV output | None |
+
+## Method 2: Using bench_gpu_time() in Python
+
+For custom benchmarking in your own code:
+
+### Step 1: Write Your Benchmark Script
+
+```python
+import torch
+from flashinfer.testing import bench_gpu_time
+
+# Setup your kernel
+def my_kernel_wrapper(q, k, v):
+    # Your kernel call here
+    return output
+
+# Create test inputs
+device = torch.device("cuda")
+q = torch.randn(32, 8, 128, dtype=torch.bfloat16, device=device)
+k = torch.randn(2048, 8, 128, dtype=torch.bfloat16, device=device)
+v = torch.randn(2048, 8, 128, dtype=torch.bfloat16, device=device)
+
+# Benchmark - CUPTI preferred, CUDA events if CUPTI unavailable
+median_time, std_time = bench_gpu_time(
+    my_kernel_wrapper,
+    args=(q, k, v),
+    enable_cupti=True,          # Prefer CUPTI, fallback to CUDA events
+    num_iters=30,               # Number of iterations
+    dry_run_iters=5,            # Warmup iterations
+)
+
+print(f"Kernel time: {median_time:.3f} ms ± {std_time:.3f} ms")
+
+# Calculate FLOPS if you know the operation count
+flops = ...  # Your FLOP count
+tflops = (flops / 1e12) / (median_time / 1000)
+print(f"Achieved: {tflops:.2f} TFLOPS/sec")
+```
+
+**Note**: If CUPTI is not installed, you'll see a warning and the function will automatically use CUDA events instead.
+
+### Step 2: Run Your Benchmark
+
+```bash
+python my_benchmark.py
+```
+
+Output with CUPTI:
+```
+Kernel time: 0.145 ms ± 0.002 ms
+Achieved: 125.3 TFLOPS/sec
+```
+
+Output without CUPTI (automatic fallback):
+```
+[WARNING] CUPTI is not installed. Try 'pip install -U cupti-python'. Falling back to CUDA events.
+Kernel time: 0.147 ms ± 0.003 ms
+Achieved: 124.1 TFLOPS/sec
+```
+
+### Step 3: Advanced Options
+
+```python
+# Cold L2 cache benchmarking (optional)
+median_time, std_time = bench_gpu_time(
+    my_kernel,
+    args=(x, y),
+    enable_cupti=True,          # Will use CUDA events if CUPTI unavailable
+    cold_l2_cache=True,         # Flush L2 or rotate buffers automatically
+    num_iters=30
+)
+
+# Force CUDA events (skip CUPTI even if installed)
+median_time, std_time = bench_gpu_time(
+    my_kernel,
+    args=(x, y),
+    enable_cupti=False,         # Explicitly use CUDA events
+    num_iters=30
+)
+```
+
+## Troubleshooting
+
+### CUPTI Warning Message
+
+**Warning**: `CUPTI is not installed. Falling back to CUDA events.`
+
+**What it means**: CUPTI is not available, using CUDA events instead
+
+**Impact**: Less accurate for very fast kernels (5-50 us) due to synchronization overhead, but becomes negligible for longer-running kernels
+
+**Solution (optional)**: Install CUPTI for best accuracy:
+```bash
+pip install -U cupti-python
+```
+
+If installation fails, check:
+- CUDA version >= 13
+- Compatible `cupti-python` version
+
+**You can still run benchmarks without CUPTI** - the framework handles this automatically.
+
+### Inconsistent Results
+
+**Problem**: Large standard deviation or varying results
+
+**Solutions**:
+1. **Increase warmup iterations**:
+   ```bash
+   --dry_run_iters 10
+   ```
+
+2. **Increase measurement iterations**:
+   ```bash
+   --num_iters 50
+   ```
+
+3. **Use cold L2 cache** (in Python):
+   ```python
+   bench_gpu_time(..., rotate_buffers=True)
+   ```
+
+4. **Disable GPU boost** (advanced):
+   ```bash
+   sudo nvidia-smi -lgc <base_clock>
+   ```
+
+### Reference Check Failures
+
+**Error**: `[ERROR] Output mismatch between backends`
+
+**What it means**: Different backends produce different results
+
+**Solutions**:
+1. **Allow mismatch and continue**:
+   ```bash
+   --allow_output_mismatch
+   ```
+
+2. **Check numerical tolerance**: Some backends use different precisions (FP32 vs FP16)
+
+3. **Investigate the difference**:
+   ```bash
+   -vv  # Very verbose mode shows tensor statistics
+   ```
+
+### Backend Not Supported
+
+**Error**: `[WARNING] fa3 for routine ... is not supported on compute capability X.X`
+
+**Solution**: Check the backend support matrix in `benchmarks/README.md` or remove that backend from `--backends` list
+
+## Best Practices
+
+1. **Install CUPTI for best accuracy** (but not required):
+   ```bash
+   pip install -U cupti-python
+   ```
+
+2. **Use reference checking** to verify correctness:
+   ```bash
+   --refcheck
+   ```
+
+3. **Use verbose mode** to see input shapes and dtypes:
+   ```bash
+   -vv
+   ```
+
+4. **Generate reproducer commands** for sharing results:
+   ```bash
+   --generate_repro_command
+   ```
+
+5. **Run multiple iterations** for statistical significance:
+   ```bash
+   --num_iters 30 --dry_run_iters 5
+   ```
+
+6. **Save results to CSV** for later analysis:
+   ```bash
+   --output_path results.csv
+   ```
+
+7. **Compare multiple backends** to find the best:
+   ```bash
+   --backends fa2 fa3 cudnn cutlass
+   ```
+
+## Quick Examples
+
+### Decode Attention (H100)
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine BatchDecodeWithPagedKVCacheWrapper \
+    --backends fa2 fa2_tc cudnn trtllm-gen \
+    --page_size 16 --batch_size 128 --s_kv 8192 \
+    --num_qo_heads 64 --num_kv_heads 8 \
+    --head_dim_qk 128 --head_dim_vo 128 \
+    --refcheck -vv --generate_repro_command
+```
+
+### Prefill Attention (Multi-head)
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine BatchPrefillWithRaggedKVCacheWrapper \
+    --backends fa2 fa3 cudnn cutlass \
+    --batch_size 16 --s_qo 1024 --s_kv 1024 \
+    --num_qo_heads 128 --num_kv_heads 128 \
+    --head_dim_qk 192 --head_dim_vo 128 \
+    --causal --random_actual_seq_len \
+    --q_dtype bfloat16 --kv_dtype bfloat16 \
+    --refcheck -vv
+```
+
+### FP8 GEMM (Batched)
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine bmm_fp8 \
+    --backends cudnn cublas cutlass \
+    --batch_size 256 --m 1 --n 1024 --k 7168 \
+    --input_dtype fp8_e4m3 --mat2_dtype fp8_e4m3 \
+    --out_dtype bfloat16 \
+    --refcheck -vv
+```
+
+### MOE (DeepSeek-style routing)
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine trtllm_fp8_block_scale_moe \
+    --backends trtllm \
+    --num_tokens 1024 --hidden_size 5120 \
+    --intermediate_size 13824 --num_experts 256 \
+    --top_k 8 --n_group 8 --topk_group 1 \
+    --routing_method deepseek_v3 \
+    --routed_scaling_factor 2.5 \
+    --use_routing_bias \
+    -vv
+```
+
+## Summary: CUPTI vs CUDA Events
+
+| Aspect | CUPTI (Preferred) | CUDA Events (Fallback) |
+|--------|-------------------|------------------------|
+| **Accuracy** | Highest (hardware-level) | Good (slight overhead) |
+| **Installation** | `pip install cupti-python` | Built-in with CUDA |
+| **Requirements** | CUDA 13+ | Any CUDA version |
+| **Fallback** | N/A | Automatic if CUPTI unavailable |
+| **When to use** | Always (if available) | When CUPTI can't be installed |
+
+**Recommendation**: Install CUPTI for best results, but benchmarks work fine without it.
+
+## Next Steps
+
+- **Profile kernels** with `nsys` or `ncu` for detailed analysis
+- **Debug performance issues** using `FLASHINFER_LOGLEVEL=3`
+- **Compare with baselines** using reference implementations
+- **Optimize kernels** based on profiling results
+
+## Related Documentation
+
+- See `benchmarks/README.md` for full flag documentation
+- See `benchmarks/samples/sample_testlist.txt` for more examples
+- See CLAUDE.md "Benchmarking" section for technical details
diff --git a/.claude/skills/debug-cuda-crash/skill.md b/.claude/skills/debug-cuda-crash/skill.md
@@ -0,0 +1,569 @@
+# Tutorial: Debugging CUDA Crashes with API Logging
+
+This tutorial shows you how to debug CUDA crashes and errors in FlashInfer using the `@flashinfer_api` logging decorator.
+
+## Goal
+
+When your code crashes with CUDA errors (illegal memory access, out-of-bounds, NaN/Inf), use API logging to:
+- Capture input tensors BEFORE the crash occurs
+- Understand what data caused the problem
+- Track tensor shapes, dtypes, and values through your pipeline
+- Detect numerical issues (NaN, Inf, wrong shapes)
+
+## Why Use API Logging?
+
+**Problem**: CUDA errors often crash the program, leaving no debugging information.
+
+**Solution**: FlashInfer's `@flashinfer_api` decorator logs inputs BEFORE execution, so you can see what caused the crash even after the program terminates.
+
+## Step 1: Enable API Logging
+
+### Basic Logging (Function Names Only)
+
+```bash
+export FLASHINFER_LOGLEVEL=1        # Log function names
+export FLASHINFER_LOGDEST=stdout    # Log to console
+
+python my_script.py
+```
+
+Output:
+```
+[2025-12-18 10:30:45] FlashInfer API Call: batch_decode_with_padded_kv_cache
+```
+
+### Detailed Logging (Inputs/Outputs with Metadata)
+
+```bash
+export FLASHINFER_LOGLEVEL=3        # Log inputs/outputs with metadata
+export FLASHINFER_LOGDEST=debug.log # Save to file
+
+python my_script.py
+```
+
+Output in `debug.log`:
+```
+================================================================================
+[2025-12-18 10:30:45] FlashInfer API Logging - System Information
+================================================================================
+FlashInfer version: 0.6.0
+CUDA toolkit version: 12.1
+GPU 0: NVIDIA H100 PCIe
+  Compute capability: 9.0 (SM90)
+PyTorch version: 2.1.0
+================================================================================
+
+================================================================================
+[2025-12-18 10:30:46] FlashInfer API Call: batch_decode_with_padded_kv_cache
+--------------------------------------------------------------------------------
+Positional input arguments:
+  arg[0]:
+    Tensor(
+      shape=(32, 8, 128)
+      dtype=torch.bfloat16
+      device=cuda:0
+      requires_grad=False
+      is_contiguous=True
+    )
+Keyword input arguments:
+  kv_cache=
+    Tensor(
+      shape=(1024, 2, 8, 128)
+      dtype=torch.bfloat16
+      device=cuda:0
+      requires_grad=False
+      is_contiguous=True
+    )
+```
+
+### Full Logging (With Tensor Statistics)
+
+```bash
+export FLASHINFER_LOGLEVEL=5        # Log with min/max/mean/nan/inf
+export FLASHINFER_LOGDEST=debug.log
+
+python my_script.py
+```
+
+Additional output:
+```
+  Tensor(
+    shape=(32, 8, 128)
+    dtype=torch.bfloat16
+    device=cuda:0
+    requires_grad=False
+    is_contiguous=True
+    min=-3.125000
+    max=4.250000
+    mean=0.015625
+    nan_count=0
+    inf_count=0
+  )
+```
+
+## Step 2: Reproduce the Crash
+
+### Example: Shape Mismatch
+
+Your code crashes with:
+```
+RuntimeError: CUDA error: an illegal memory access was encountered
+```
+
+Enable logging and run again:
+
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=crash_log.txt
+
+python my_script.py
+```
+
+The log shows inputs before the crash:
+```
+[2025-12-18 10:32:15] FlashInfer API Call: batch_decode_with_padded_kv_cache
+Positional input arguments:
+  arg[0]:
+    Tensor(
+      shape=(32, 8, 128)      # Query tensor
+      ...
+    )
+Keyword input arguments:
+  kv_cache=
+    Tensor(
+      shape=(1024, 2, 8, 64)  # ❌ Wrong! Should be (..., 128) not (..., 64)
+      ...
+    )
+```
+
+**Found the bug**: `head_dim` mismatch (64 vs 128)
+
+## Step 3: Common CUDA Errors and How to Debug
+
+### Error 1: Illegal Memory Access
+
+**Error Message**:
+```
+RuntimeError: CUDA error: an illegal memory access was encountered
+```
+
+**Enable logging**:
+```bash
+export FLASHINFER_LOGLEVEL=3
+python my_script.py
+```
+
+**What to check in logs**:
+- ✅ Tensor shapes match expected dimensions
+- ✅ All tensors are on CUDA (not CPU)
+- ✅ Tensor strides are reasonable
+- ✅ `is_contiguous=True` (if required)
+
+**Common causes**:
+- Wrong tensor dimensions
+- CPU tensor passed to GPU kernel
+- Incorrect stride patterns
+
+### Error 2: NaN or Inf Values
+
+**Error Message**:
+```
+RuntimeError: Function ... returned nan or inf
+```
+
+**Enable statistics logging**:
+```bash
+export FLASHINFER_LOGLEVEL=5        # Level 5 shows nan_count, inf_count
+python my_script.py
+```
+
+**What to check in logs**:
+```
+Tensor(
+  ...
+  min=-1234567.000000     # ❌ Suspiciously large
+  max=9876543.000000      # ❌ Suspiciously large
+  mean=nan                # ❌ NaN detected
+  nan_count=128           # ❌ 128 NaN values!
+  inf_count=0
+)
+```
+
+**Common causes**:
+- Division by zero in previous operation
+- Numerical overflow/underflow
+- Uninitialized memory
+
+### Error 3: Out of Memory
+
+**Error Message**:
+```
+RuntimeError: CUDA out of memory
+```
+
+**Enable logging**:
+```bash
+export FLASHINFER_LOGLEVEL=3
+python my_script.py
+```
+
+**What to check in logs**:
+- ✅ Tensor shapes (are they unexpectedly large?)
+- ✅ Batch size
+- ✅ Sequence length
+
+Example:
+```
+Tensor(
+  shape=(1024, 8192, 128, 128)  # ❌ Way too large! Should be (1024, 128, 128)?
+  ...
+)
+```
+
+### Error 4: Wrong Dtype
+
+**Error Message**:
+```
+RuntimeError: expected scalar type BFloat16 but found Float16
+```
+
+**Enable logging**:
+```bash
+export FLASHINFER_LOGLEVEL=3
+python my_script.py
+```
+
+**What to check in logs**:
+```
+Tensor(
+  dtype=torch.float16     # ❌ Should be torch.bfloat16
+  ...
+)
+```
+
+## Step 4: Multi-Process Debugging
+
+When running with multiple GPUs/processes, use `%i` pattern:
+
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=debug_rank_%i.txt    # %i = process ID
+
+torchrun --nproc_per_node=4 my_script.py
+```
+
+This creates separate logs:
+- `debug_rank_12345.txt` (process 12345)
+- `debug_rank_12346.txt` (process 12346)
+- `debug_rank_12347.txt` (process 12347)
+- `debug_rank_12348.txt` (process 12348)
+
+Now you can debug each rank independently.
+
+## Step 5: Advanced Debugging with compute-sanitizer
+
+For harder bugs, combine API logging with CUDA tools:
+
+### Use compute-sanitizer (Memory Checker)
+
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=debug.log
+
+compute-sanitizer --tool memcheck python my_script.py
+```
+
+Output shows exact memory errors:
+```
+========= COMPUTE-SANITIZER
+========= Invalid __global__ write of size 4 bytes
+=========     at 0x1234 in ScaleKernel<float>
+=========     by thread (256,0,0) in block (10,0,0)
+=========     Address 0x7f1234567890 is out of bounds
+```
+
+Check `debug.log` to see what inputs caused this kernel to fail.
+
+### Use cuda-gdb (Debugger)
+
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=debug.log
+
+cuda-gdb --args python my_script.py
+```
+
+In gdb:
+```
+(cuda-gdb) run
+(cuda-gdb) where     # Show stack trace when it crashes
+```
+
+Check `debug.log` for the inputs that led to the crash.
+
+## Step 6: Kernel-Level Debugging with printf()
+
+You can use `printf()` inside CUDA kernels for debugging:
+
+### Basic Usage
+
+```cpp
+__global__ void MyKernel(const float* input, float* output, int n) {
+  int idx = blockIdx.x * blockDim.x + threadIdx.x;
+
+  // Print from one thread to avoid spam
+  if (threadIdx.x == 0 && blockIdx.x == 0) {
+    printf("n=%d, input[0]=%f\n", n, input[0]);
+  }
+
+  if (idx < n) {
+    output[idx] = input[idx] * 2.0f;
+  }
+}
+```
+
+**Important**: Flush printf buffer after kernel:
+```python
+my_kernel(input, output)
+torch.cuda.synchronize()  # ← Flushes printf output
+```
+
+### ⚠️ Warp-Specialized Kernels: Choosing the Right Print Thread
+
+**Problem**: `threadIdx.x == 0` doesn't work for all warps (warp starting at thread 32 won't have thread 0).
+
+**Solution**: Choose one representative thread per specialization group.
+
+```cpp
+__global__ void WarpSpecializedKernel(...) {
+  // Define your group's representative thread
+  // e.g., first thread of each warp: threadIdx.x % 32 == 0
+  // e.g., first thread of each 4-warp group: threadIdx.x % 128 == 0
+
+  if (is_group_representative) {
+    printf("Group %d processing\n", group_id);
+  }
+}
+```
+
+**Common mistake** ❌:
+```cpp
+// ❌ Only warp 0 will print!
+if (threadIdx.x == 0) {
+  printf("Warp %d processing\n", threadIdx.x / 32);
+}
+```
+
+### Quick Reference
+
+| Kernel Type | Print Condition | Notes |
+|-------------|-----------------|-------|
+| Simple kernel | `threadIdx.x == 0` | One thread per block |
+| Warp-specialized | One thread per group | Depends on kernel design |
+
+### Other Kernel Debugging Tools
+
+```cpp
+// Assert for invariants
+assert(value >= 0.0f && "Value must be non-negative");
+
+// Compile-time checks
+static_assert(BLOCK_SIZE % 32 == 0, "BLOCK_SIZE must be multiple of warp size");
+```
+
+## Environment Variables Reference
+
+| Variable | Values | Description |
+|----------|--------|-------------|
+| `FLASHINFER_LOGLEVEL` | `0` | No logging (default) |
+|  | `1` | Function names only |
+|  | `3` | Inputs/outputs with metadata |
+|  | `5` | + Tensor statistics (min/max/mean/nan/inf) |
+| `FLASHINFER_LOGDEST` | `stdout` | Log to console (default) |
+|  | `stderr` | Log to stderr |
+|  | `<path>` | Log to file |
+|  | `log_%i.txt` | Multi-process: %i = process ID |
+
+## Best Practices
+
+### 1. Always Start with Level 3
+
+```bash
+export FLASHINFER_LOGLEVEL=3
+```
+
+Level 3 provides tensor metadata (shape, dtype, device) without overwhelming output.
+
+### 2. Use Level 5 for Numerical Issues
+
+```bash
+export FLASHINFER_LOGLEVEL=5
+```
+
+Only use level 5 when debugging NaN/Inf problems (adds statistics).
+
+### 3. Log to File for Crashes
+
+```bash
+export FLASHINFER_LOGDEST=crash_log.txt
+```
+
+Console output may be lost when program crashes. File logs persist.
+
+### 4. Compare Before/After
+
+Enable logging and compare:
+- Last successful API call (inputs logged, outputs logged) ✅
+- First failed API call (inputs logged, no outputs) ❌ ← This is where it crashed!
+
+### 5. Disable Logging in Production
+
+```bash
+unset FLASHINFER_LOGLEVEL   # or export FLASHINFER_LOGLEVEL=0
+```
+
+Logging has zero overhead when disabled (decorator returns original function).
+
+## Troubleshooting
+
+### No Logs Appearing
+
+**Problem**: Set `FLASHINFER_LOGLEVEL=3` but no logs appear
+
+**Solutions**:
+1. **Check if API has the decorator**: Not all FlashInfer APIs have `@flashinfer_api` yet (work in progress)
+
+2. **Verify environment variable**:
+   ```bash
+   echo $FLASHINFER_LOGLEVEL    # Should print "3"
+   ```
+
+3. **Check log destination**:
+   ```bash
+   echo $FLASHINFER_LOGDEST     # Should print path or "stdout"
+   ```
+
+### Too Much Output
+
+**Problem**: Level 5 produces too much output
+
+**Solution**: Use level 3 instead:
+```bash
+export FLASHINFER_LOGLEVEL=3   # Skip tensor statistics
+```
+
+### Statistics Skipped in CUDA Graph
+
+**Warning**: `[statistics skipped: CUDA graph capture in progress]`
+
+**What it means**: Level 5 statistics are automatically skipped during CUDA graph capture (to avoid synchronization)
+
+**This is normal**: The framework protects you from graph capture issues.
+
+## Quick Examples
+
+### Debug Shape Mismatch
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=stdout
+python my_script.py
+# Check tensor shapes in output
+```
+
+### Debug NaN/Inf
+```bash
+export FLASHINFER_LOGLEVEL=5         # Show statistics
+export FLASHINFER_LOGDEST=debug.log
+python my_script.py
+# Check nan_count and inf_count in debug.log
+```
+
+### Debug Multi-GPU Training
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=rank_%i.log   # Separate log per rank
+torchrun --nproc_per_node=8 train.py
+# Check rank_*.log files
+```
+
+### Combine with Memory Checker
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=inputs.log
+compute-sanitizer --tool memcheck python my_script.py
+# inputs.log shows what data caused the memory error
+```
+
+## Example: Full Debug Session
+
+### Your code crashes:
+```python
+import torch
+from flashinfer import batch_decode_with_padded_kv_cache
+
+q = torch.randn(32, 8, 128, dtype=torch.bfloat16, device="cuda")
+kv = torch.randn(1024, 2, 8, 64, dtype=torch.bfloat16, device="cuda")  # Wrong dim!
+
+output = batch_decode_with_padded_kv_cache(q, kv)  # ❌ Crashes
+```
+
+### Enable logging:
+```bash
+export FLASHINFER_LOGLEVEL=3
+export FLASHINFER_LOGDEST=debug.log
+python test.py
+```
+
+### Check debug.log:
+```
+[2025-12-18 10:45:23] FlashInfer API Call: batch_decode_with_padded_kv_cache
+Positional input arguments:
+  arg[0]:
+    Tensor(
+      shape=(32, 8, 128)
+      dtype=torch.bfloat16
+      ...
+    )
+  arg[1]:
+    Tensor(
+      shape=(1024, 2, 8, 64)    # ❌ Found it! Last dim should be 128
+      dtype=torch.bfloat16
+      ...
+    )
+```
+
+### Fix the bug:
+```python
+kv = torch.randn(1024, 2, 8, 128, dtype=torch.bfloat16, device="cuda")  # ✅ Fixed
+```
+
+### Success!
+```bash
+python test.py
+# No crash, outputs logged successfully
+```
+
+## Summary
+
+1. **Enable logging** before the crash:
+   ```bash
+   export FLASHINFER_LOGLEVEL=3
+   export FLASHINFER_LOGDEST=debug.log
+   ```
+
+2. **Run your code** - inputs are logged BEFORE crash
+
+3. **Check the log** - last API call shows what caused the crash
+
+4. **Fix the issue** based on logged input metadata
+
+5. **Disable logging** when done:
+   ```bash
+   export FLASHINFER_LOGLEVEL=0
+   ```
+
+## Related Documentation
+
+- See CLAUDE.md "API Logging with @flashinfer_api" for technical details
+- See `flashinfer/api_logging.py` for implementation
+- See CUDA documentation for compute-sanitizer and cuda-gdb
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,553 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Project Overview
+
+FlashInfer is a GPU kernel library for LLM serving that uses **JIT (Just-In-Time) compilation by default**. This means kernel code changes are automatically picked up without reinstalling the package - extremely convenient for development.
+
+## Quick Reference
+
+| Task | Command |
+|------|---------|
+| Install for development | `pip install --no-build-isolation -e . -v` |
+| Initialize submodules | `git submodule update --init --recursive` |
+| Install CUPTI for benchmarking | `pip install -U cupti-python` |
+| Run all tests | `pytest tests/` |
+| Run specific test | `pytest tests/path/test_file.py::test_function` |
+| Run multi-GPU test | `mpirun -np 4 pytest tests/comm/test_allreduce_unified_api.py` |
+| Run benchmark | `python benchmarks/flashinfer_benchmark.py --routine <name> <flags>` |
+| Run linting | `pre-commit run -a` |
+| Install pre-commit hooks | `pre-commit install` |
+| Clear JIT cache | `rm -rf ~/.cache/flashinfer/` |
+| Enable API logging (basic) | `export FLASHINFER_LOGLEVEL=1` |
+| Enable API logging (detailed) | `export FLASHINFER_LOGLEVEL=3` |
+| Enable API logging (with stats) | `export FLASHINFER_LOGLEVEL=5` |
+| Set API log destination | `export FLASHINFER_LOGDEST=mylog.txt` |
+| Enable verbose JIT logging | `export FLASHINFER_JIT_VERBOSE=1` |
+| Enable debug build | `export FLASHINFER_JIT_DEBUG=1` |
+| Set target architectures | `export FLASHINFER_CUDA_ARCH_LIST="8.0 9.0a"` |
+| Set parallel compilation | `export FLASHINFER_NVCC_THREADS=4` |
+
+## Quick Start for Development
+
+### Installation
+
+```bash
+git clone https://github.com/flashinfer-ai/flashinfer.git --recursive
+cd flashinfer
+pip install --no-build-isolation -e . -v
+```
+
+**Important**: The `--recursive` flag is required to initialize submodules in `3rdparty/` (cutlass, spdlog).
+
+If you forgot `--recursive` when cloning:
+```bash
+git submodule update --init --recursive
+```
+
+That's it! You can now:
+
+- Run all benchmarks and unit tests
+- Modify kernel source code in `include/` without reinstalling
+- Changes are JIT-compiled on next use
+
+The `--no-build-isolation` flag prevents pip from pulling incompatible PyTorch/CUDA versions from PyPI.
+
+### How JIT Compilation Works
+
+When you call a FlashInfer API:
+
+1. **First call**: Generates specialized CUDA code based on parameters (dtype, head_dim, etc.), compiles it with ninja, caches the .so file
+2. **Subsequent calls**: Uses cached compiled module
+3. **After kernel changes**: Automatically detects changes and recompiles
+
+**No manual rebuild step needed** - just edit `.cuh` files and run your code again.
+
+### Pre-compiled Packages (Optional)
+
+FlashInfer provides optional pre-compiled packages for users who want faster initialization:
+
+- `flashinfer-jit-cache`: Pre-built kernel cache
+- `flashinfer-cubin`: Pre-compiled kernel binaries
+
+**For development, you typically DON'T need these.** JIT compilation is fast enough and gives you live code reload.
+
+## Testing
+
+Run all tests:
+
+```bash
+pytest tests/
+```
+
+Run specific test file:
+
+```bash
+pytest tests/attention/test_hopper.py
+```
+
+Run specific test function:
+
+```bash
+pytest tests/attention/test_hopper.py::test_single_prefill
+```
+
+### Skipping Tests Based on CUDA Architecture
+
+Use `flashinfer.utils` functions to skip tests on unsupported GPU architectures:
+
+**Available check functions:**
+- `get_compute_capability(device)` - Returns `(major, minor)` tuple
+- `is_sm90a_supported()` - Hopper (requires CUDA 12.3+)
+- `is_sm100a_supported()` - Blackwell (requires CUDA 12.8+)
+- `is_sm110a_supported()`, `is_sm120a_supported()`, `is_sm121a_supported()`
+
+**APIs decorated with `@backend_requirement`** also provide:
+- `api_name.is_compute_capability_supported(cc)` - e.g., `mm_fp4.is_compute_capability_supported(100)`
+- `api_name.is_backend_supported("backend")` - e.g., `mm_fp4.is_backend_supported("cudnn")`
+- `api_name.is_backend_supported("backend", cc)` - e.g., `mm_fp4.is_backend_supported("cudnn", 80)`
+
+**Example:**
+```python
+from flashinfer.utils import is_sm90a_supported
+
+def test_hopper_attention():
+    if not is_sm90a_supported(torch.device("cuda")):
+        pytest.skip("Requires SM90a")
+    # Test code...
+```
+
+**Common requirements:**
+
+| Feature | Min SM | Check Function |
+|---------|--------|----------------|
+| FlashAttention-3 | SM90a | `is_sm90a_supported()` |
+| MLA Attention | SM100a | `is_sm100a_supported()` |
+| FP8 GEMM | SM89+ | `get_compute_capability()[0] >= 9` |
+
+**Note:** `tests/conftest.py` auto-skips tests that trigger OOM, but tests should be written to avoid OOM by using appropriate problem sizes.
+
+## Benchmarking
+
+FlashInfer provides a unified benchmarking framework in `benchmarks/flashinfer_benchmark.py`.
+
+**Key features:**
+- Supports attention, GEMM, and MOE kernels
+- Multiple backends: FlashAttention2/3, cuDNN, CUTLASS, TensorRT-LLM, cuBLAS
+- **CUPTI timing (recommended)**: Hardware-level profiling for accurate GPU kernel time
+  - Automatically falls back to CUDA events if CUPTI unavailable
+  - Install: `pip install -U cupti-python` (requires CUDA 13+)
+- Batch testing, reference checking, CSV output
+
+**Quick example:**
+```bash
+python benchmarks/flashinfer_benchmark.py \
+    --routine BatchDecodeWithPagedKVCacheWrapper \
+    --backends fa2 cudnn \
+    --batch_size 32 --s_kv 2048 \
+    --num_qo_heads 32 --num_kv_heads 8 \
+    --head_dim_qk 128 --head_dim_vo 128 \
+    --page_size 16 --refcheck -vv
+```
+
+**Python API:**
+```python
+from flashinfer.testing import bench_gpu_time
+
+# CUPTI preferred, auto-fallback to CUDA events
+median_time, std_time = bench_gpu_time(
+    my_kernel, args=(x, y), enable_cupti=True, num_iters=30
+)
+```
+
+→ **For complete benchmarking guide, see [`.claude/skills/benchmark-kernel/skill.md`](.claude/skills/benchmark-kernel/skill.md)**
+
+## Code Linting
+
+Run all pre-commit hooks:
+
+```bash
+pre-commit run -a
+```
+
+Install hooks to run on every commit:
+
+```bash
+pre-commit install
+```
+
+## Architecture: JIT Compilation System
+
+FlashInfer's JIT system has three layers:
+
+### Layer 1: JitSpec (flashinfer/jit/core.py)
+
+`JitSpec` defines compilation metadata:
+
+- `name`: Unique identifier (URI hash from parameters)
+- `sources`: List of .cu/.cpp files to compile
+- `extra_cuda_cflags`, `extra_cflags`, `extra_ldflags`: Compiler flags
+
+### Compilation Context: Architecture-Specific Compilation
+
+FlashInfer uses `CompilationContext` to manage CUDA architecture targets. Some kernels only work on specific GPU architectures (e.g., Hopper SM90, Blackwell SM100/SM12x).
+
+**How it works:**
+- Auto-detects GPUs in system or reads `FLASHINFER_CUDA_ARCH_LIST` environment variable
+- JIT modules specify `supported_major_versions=[9, 10, 11, 12]` to limit compilation to specific SM versions
+- If GPU not supported → `RuntimeError: No supported CUDA architectures found`
+
+→ **See [`.claude/skills/add-cuda-kernel/skill.md`](.claude/skills/add-cuda-kernel/skill.md) for usage examples**
+
+### Layer 2: Code Generation
+
+Every `gen_*_module()` function in `flashinfer/jit/` follows this pattern:
+
+```python
+def gen_some_module(dtype_in, dtype_out, ...):
+    # 1. Compute unique identifier from parameters
+    uri = get_some_uri(dtype_in, dtype_out, ...)
+
+    # 2. Create generation directory
+    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
+
+    # 3. (Optional) Render Jinja template to generate type-specialized config
+    # Skip this step if you don't need type specialization
+    with open(jit_env.FLASHINFER_CSRC_DIR / "some_customize_config.jinja") as f:
+        template = jinja2.Template(f.read())
+    config_content = template.render(
+        dtype_in=dtype_map[dtype_in],
+        dtype_out=dtype_map[dtype_out],
+        # ... more parameters
+    )
+    write_if_different(gen_directory / "some_config.inc", config_content)
+
+    # 4. Copy source files to gen directory
+    sources = []
+    for fname in ["some_kernel.cu", "some_jit_binding.cu"]:
+        shutil.copy(jit_env.FLASHINFER_CSRC_DIR / fname, gen_directory / fname)
+        sources.append(gen_directory / fname)
+
+    # 5. Return JitSpec
+    return gen_jit_spec(uri, sources, extra_cuda_cflags=[...])
+```
+
+**Note**: If your operation doesn't need type specialization, you can skip step 3 entirely and just copy the source files directly.
+
+### Layer 3: Compilation and Loading
+
+`JitSpec` methods:
+
+- `write_ninja()` - Generates `build.ninja` file
+- `build()` - Executes `ninja` to compile sources
+- `build_and_load()` - Compiles and loads via TVM-FFI
+
+The generated `build.ninja` file uses nvcc to compile .cu → .cuda.o → .so, then loads via TVM-FFI.
+
+### Jinja Templates (Optional)
+
+**Note: Jinja templates are NOT required.** You can write C++ code directly without templating.
+
+For operations that need type specialization, templates in `csrc/*.jinja` can generate C++ code:
+
+```jinja
+// Input template
+using DTypeIn = {{ dtype_in }};
+using DTypeOut = {{ dtype_out }};
+constexpr int PARAM = {{ param_value }};
+
+// After render
+using DTypeIn = float16;
+using DTypeOut = float16;
+constexpr int PARAM = 128;
+```
+
+This allows the same CUDA template code to be compiled with different concrete types. However, if your operation doesn't need this, you can skip Jinja and write the `.cu` files directly.
+
+## Directory Structure
+
+```
+flashinfer/
+├── include/flashinfer/           # Header-only CUDA kernel templates
+│   ├── attention/                # Attention kernels
+│   ├── gemm/                     # GEMM kernels
+│   ├── comm/                     # Communication kernels
+│   ├── mma.cuh                   # Matrix multiply utilities
+│   ├── utils.cuh                 # Common utilities
+│   └── [...]
+│
+├── csrc/                          # Framework bindings (via TVM-FFI)
+│   ├── *.cu                       # Kernel launcher implementations
+│   ├── *_jit_binding.cu           # TVM-FFI exports
+│   ├── *_customize_config.jinja   # Type config templates (optional)
+│   └── [...]
+│
+├── flashinfer/                    # Python package
+│   ├── jit/
+│   │   ├── core.py                # JitSpec, compilation infrastructure
+│   │   ├── cpp_ext.py             # Ninja build generation
+│   │   ├── env.py                 # Workspace paths
+│   │   ├── attention/             # Attention module generators
+│   │   ├── gemm/                  # GEMM module generators
+│   │   ├── fused_moe/             # MOE module generators
+│   │   └── [...]
+│   ├── gemm/                      # GEMM Python APIs
+│   ├── fused_moe/                 # MOE Python APIs
+│   ├── comm/                      # Communication Python APIs
+│   ├── *.py                       # Other high-level Python APIs
+│   ├── aot.py                     # AOT compilation for pre-built packages
+│   └── [...]
+│
+├── tests/                         # Test suite
+│   ├── attention/                 # Attention kernel tests
+│   ├── gemm/                      # GEMM kernel tests
+│   ├── moe/                       # MOE kernel tests
+│   ├── comm/                      # Communication tests
+│   ├── utils/                     # Utility tests
+│   └── conftest.py                # Pytest configuration
+│
+└── build_backend.py               # PEP 517 build backend
+```
+
+### Critical Rule: Framework Separation
+
+**Torch headers MUST NOT be included in `include/` directory files.**
+
+- `include/`: Framework-agnostic CUDA kernels (accept raw pointers)
+- `csrc/`: Framework bindings via TVM-FFI (currently PyTorch, but can support other frameworks)
+
+## Adding a New Operation
+
+→ **For complete step-by-step tutorial, see [`.claude/skills/add-cuda-kernel/skill.md`](.claude/skills/add-cuda-kernel/skill.md)**
+
+**Quick overview of the process:**
+1. Write kernel in `include/flashinfer/new_op.cuh` (framework-agnostic, raw pointers)
+2. Write launcher in `csrc/new_op.cu` (PyTorch tensor handling)
+3. Create TVM-FFI bindings in `csrc/new_op_jit_binding.cu`
+4. (Optional) Create Jinja template for type specialization
+5. Write JIT module generator in `flashinfer/jit/new_op.py`
+6. Write Python API in `flashinfer/new_op.py` with `@functools.cache`
+7. Write tests in `tests/`
+8. Register in `flashinfer/aot.py` for AOT compilation
+9. Export in `flashinfer/__init__.py`
+
+**Example implementations:**
+- **Simple**: `flashinfer/norm.py` (RMSNorm) - no Jinja, good starting point
+- **Moderate**: `flashinfer/sampling.py` - with Jinja templating
+- **Complex**: `flashinfer/decode.py` - plan-run pattern, advanced workspace
+
+## Key Architectural Patterns
+
+### Module Caching
+
+FlashInfer uses two-level caching to avoid recompilation:
+
+1. **Python-level** (`@functools.cache`): In-memory cache of loaded modules
+2. **File-level** (`~/.cache/flashinfer/`): Compiled `.so` files on disk
+
+**Cache invalidation** (automatic):
+- Source file changes (SHA256 hash)
+- Compilation flags change
+- CUDA architecture change
+- FlashInfer version change
+
+URI computed as: `hash(operation_type + parameters + source_hashes + flags + cuda_arch)`
+
+**Cache management:**
+- Clear cache: `rm -rf ~/.cache/flashinfer/`
+- Override location: `export FLASHINFER_WORKSPACE_BASE="/scratch"`
+
+### Dispatch Macros
+
+Handle combinatorial parameter spaces:
+
+```cpp
+DISPATCH_DTYPE(input_dtype, DTypeIn, {
+  DISPATCH_DTYPE(output_dtype, DTypeOut, {
+    DISPATCH_BLOCK_SIZE(block_size, BLOCK_SIZE, {
+      LaunchKernel<DTypeIn, DTypeOut, BLOCK_SIZE>(...);
+    });
+  });
+});
+```
+
+Defined in `.jinja` files and expanded after rendering.
+
+## API Logging with @flashinfer_api
+
+FlashInfer provides the `@flashinfer_api` decorator for debugging API calls.
+
+**Key features:**
+- **Crash-safe**: Logs inputs BEFORE execution (preserves info even if kernel crashes)
+- **Zero overhead when disabled**: `FLASHINFER_LOGLEVEL=0` (default)
+- **Multiple verbosity levels**: 0 (off), 1 (names), 3 (inputs/outputs), 5 (+ statistics)
+- **CUDA graph compatible**: Auto-skips stats during graph capture
+
+**Quick usage:**
+```bash
+# Enable detailed logging
+export FLASHINFER_LOGLEVEL=3              # 0, 1, 3, or 5
+export FLASHINFER_LOGDEST=debug.log       # stdout, stderr, or file path
+
+python my_script.py
+```
+
+**Why use this?**
+- Debug CUDA crashes (see inputs that caused crash)
+- Track tensor shapes/dtypes through pipeline
+- Detect NaN/Inf issues (level 5)
+
+→ **For complete debugging guide, see [`.claude/skills/debug-cuda-crash/skill.md`](.claude/skills/debug-cuda-crash/skill.md)**
+
+## Debugging
+
+### Enable Logging
+
+```bash
+export FLASHINFER_JIT_VERBOSE=1      # Verbose JIT output
+export FLASHINFER_JIT_DEBUG=1        # Debug symbols, -O0
+export FLASHINFER_LOGLEVEL=3         # API logging (0=off, 1=basic, 3=detailed)
+export FLASHINFER_LOGDEST=stdout
+```
+
+### Inspect Generated Code
+
+```bash
+# Generated sources
+ls -la ~/.cache/flashinfer/0.6.0/*/generated/
+
+# Compiled modules
+ls -la ~/.cache/flashinfer/0.6.0/*/cached_ops/
+
+# Build files
+cat ~/.cache/flashinfer/0.6.0/*/cached_ops/*/build.ninja
+```
+
+### Environment Variables
+
+```bash
+# Compilation
+export FLASHINFER_NVCC_THREADS=4              # Parallel compilation
+export FLASHINFER_CUDA_ARCH_LIST="8.0 9.0a"  # Target architectures
+
+# Behavior
+export FLASHINFER_WORKSPACE_BASE="/scratch"   # Custom cache directory
+```
+
+## Development Workflow
+
+### Typical Development Loop
+
+1. Edit kernel code in `include/flashinfer/some_kernel.cuh`
+2. Run test: `pytest tests/test_some_kernel.py::test_specific_case`
+3. FlashInfer detects changes and recompiles automatically
+4. No `pip install` needed!
+
+### Modifying Existing Kernels
+
+- **Kernel templates**: `include/flashinfer/**/*.cuh` - Changes picked up on next JIT compile
+- **Launcher code**: `csrc/*.cu` - May need changes if adding new template parameters
+- **Jinja templates**: `csrc/*.jinja` - Update if adding new config parameters
+- **Python API**: `flashinfer/*.py` - Update if changing function signatures
+
+### Creating Pre-compiled Packages
+
+When ready to distribute:
+
+```bash
+# Build flashinfer-jit-cache package
+cd flashinfer-jit-cache
+export FLASHINFER_CUDA_ARCH_LIST="7.5 8.0 8.9 9.0a 10.0a 11.0a 12.0f"
+python -m build --no-isolation --wheel
+```
+
+This runs `flashinfer/aot.py` which calls all registered `gen_*_module()` functions and pre-compiles them.
+
+## Build System Details
+
+- **Build backend**: Custom PEP 517 backend in `build_backend.py`
+- **Data directories**: Build creates symlinks for editable installs:
+  - `3rdparty/cutlass` → `flashinfer/data/cutlass`
+  - `csrc` → `flashinfer/data/csrc`
+  - `include` → `flashinfer/data/include`
+- **Version**: Generated in `flashinfer/_build_meta.py` from `version.txt`
+
+## External Integrations
+
+### TVM-FFI: Cross-Language Unified ABI
+
+FlashInfer uses **TVM-FFI** (Apache TVM's Foreign Function Interface) for bindings, which provides a **cross-language unified ABI**. This means:
+
+- **Not limited to PyTorch**: The same compiled kernels can be used from multiple frameworks
+- **Language agnostic**: Bindings can be created for Python, C++, Rust, etc.
+- **Type-safe marshaling**: Automatic tensor/array conversion between languages
+- **Export syntax**: Use `TVM_FFI_DLL_EXPORT_TYPED_FUNC(name, func)` to expose C++ functions
+
+While FlashInfer currently provides PyTorch bindings, the underlying kernels are framework-agnostic thanks to TVM-FFI.
+
+### Other Integrations
+
+- **PyTorch Custom Ops**: `torch.library` for `torch.compile()` and CUDA graph support
+- **Ninja Build**: Direct ninja generation, no CMake complexity
+
+## Supported GPU Architectures
+
+FlashInfer supports NVIDIA SM75, SM80, SM86, SM89, SM90, SM103, SM110, SM120, and SM121.
+
+## Release Versioning
+
+FlashInfer follows a "right-shifted" versioning scheme (`major.minor.patch[.post1]`):
+
+- **major**: Architectural milestone and/or incompatible API changes (similar to PyTorch 2.0)
+- **minor**: Significant backwards-compatible new features
+- **patch**: Small backwards-compatible features (new kernels, new SM support) and backwards-compatible bug fixes
+- **post1**: Optional suffix for quick follow-up release with just backwards-compatible bug fixes
+
+## External Documentation Resources
+
+When working with FlashInfer's dependencies and tools, refer to these official documentation sources:
+
+### Core Dependencies
+
+- **TVM-FFI**: Apache TVM's Foreign Function Interface
+  - Documentation: <https://tvm.apache.org/ffi/>
+  - Package: `apache-tvm-ffi` (<https://pypi.org/project/apache-tvm-ffi/>)
+  - Use for: Understanding FFI export syntax, cross-language bindings
+
+- **CUTLASS**: NVIDIA's CUDA Templates for Linear Algebra Subroutines
+  - **Recommended**: Read source code directly in `3rdparty/cutlass/` (documentation is often outdated)
+  - Repository: <https://github.com/NVIDIA/cutlass>
+  - Use for: GEMM kernel implementations, tensor core operations
+
+- **CuTe (CUTE DSL)**: CUTLASS's Cute Layout and Tensor DSL
+  - Documentation: <https://docs.nvidia.com/cutlass/media/docs/pythonDSL/cute_dsl.html>
+  - **Tip**: Add `.md` to get Markdown format: <https://docs.nvidia.com/cutlass/media/docs/pythonDSL/cute_dsl.html.md>
+  - The Cute DSL kernels rely on Python modules from the `nvidia-cutlass-dsl` pip package, not to be confused with Python modules in the `3rdparty/cutlass` submodule
+  - Tutorial: <https://github.com/NVIDIA/cutlass/tree/main/examples/python/CuTeDSL>
+
+- **PTX ISA (Parallel Thread Execution)**: NVIDIA's PTX instruction set documentation
+  - Documentation: <https://docs.nvidia.com/cuda/parallel-thread-execution/>
+  - **Index/Table of Contents**: <https://docs.nvidia.com/cuda/parallel-thread-execution/index.html.md>
+  - **Tip**: Add `.md` to any page URL to get Markdown format
+  - Use for: Low-level instruction details, new GPU architecture features, inline PTX assembly
+
+### When to Consult These Docs
+
+- **Understanding new GPU architecture features** → Check PTX ISA documentation for latest instruction details
+- **Working on FFI bindings** → Check TVM-FFI docs for export patterns and type marshaling
+- **Implementing Tensor-Core kernels using CUTLASS** → Read source code in `3rdparty/cutlass/`
+- **Using tensor layouts or warp-level operations** → Refer to CuTe documentation
+- **Writing inline PTX assembly** → Consult PTX ISA for instruction syntax and semantics
+
+These dependencies are included in FlashInfer's `3rdparty/` directory or `requirements.txt`.
+
+### Some final suggestions for all AI agents
+
+> Because practical engineering involves the accumulated experience of trial and error, match the coding style, efficiency, complexity, verbosity, and defensiveness by learning from existing code as much as possible—this document contains many pointers on where to find examples. Document intentional departures with rationale. Mentioning "AI-assisted" in the git commit message is good transparency. For performance-critical hot paths, leave justification for the special algorithmic choices and other potential alternatives in a comment for review.
+
+**Keep documentation in sync with code changes:** When modifying code that is referenced in this document or in `.claude/skills/`, update the corresponding documentation immediately. This includes:
+- Important infrastructure changes (e.g., `@flashinfer_api`, `@backend_requirement`, TVM-FFI macros) → Update examples in `CLAUDE.md` and relevant skill files
+- New patterns or conventions → Document them for future reference
+- Deprecated approaches → Remove or mark as deprecated in docs
+- New error handling patterns, macros, or utilities → Add to relevant skill tutorials
PATCH

echo "Gold patch applied."
