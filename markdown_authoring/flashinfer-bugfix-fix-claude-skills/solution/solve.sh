#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flashinfer

# Idempotency guard
if grep -qF "**All new kernels should have benchmarks.** This helps track performance regress" ".claude/skills/add-cuda-kernel/SKILL.md" && grep -qF "description: Guide for benchmarking FlashInfer kernels with CUPTI timing" ".claude/skills/benchmark-kernel/SKILL.md" && grep -qF "description: Tutorial for debugging CUDA crashes using API logging" ".claude/skills/debug-cuda-crash/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-cuda-kernel/SKILL.md b/.claude/skills/add-cuda-kernel/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: add-cuda-kernel
+description: Step-by-step tutorial for adding new CUDA kernels to FlashInfer
+---
+
 # Tutorial: Adding a New Kernel to FlashInfer
 
 This tutorial walks through adding a simple element-wise scale operation to FlashInfer. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.
@@ -736,6 +741,55 @@ pytest tests/test_scale.py -v
 pytest tests/test_scale.py::test_scale_correctness[float16-128] -v
 ```
 
+## Step 10: Add Benchmark
+
+**All new kernels should have benchmarks.** This helps track performance regressions and allows users to compare against other implementations.
+
+Create a benchmark file in `benchmarks/` (e.g., `benchmarks/bench_scale.py`):
+
+```python
+import torch
+from flashinfer.testing import bench_gpu_time
+
+def bench_scale():
+    """Benchmark scale kernel."""
+    import flashinfer
+
+    sizes = [1024, 4096, 16384, 65536, 262144]
+    dtypes = [torch.float16, torch.bfloat16]
+
+    print("Scale Kernel Benchmark")
+    print("-" * 60)
+    print(f"{'Size':>10} {'Dtype':>10} {'Time (us)':>12} {'Std (us)':>10}")
+    print("-" * 60)
+
+    for size in sizes:
+        for dtype in dtypes:
+            x = torch.randn(size, dtype=dtype, device="cuda")
+
+            # Benchmark with CUPTI (auto-fallback to CUDA events)
+            median_time, std_time = bench_gpu_time(
+                flashinfer.scale,
+                args=(x, 2.0),
+                enable_cupti=True,
+                dry_run_iters=10,
+                repeat_iters=100,
+            )
+
+            print(f"{size:>10} {str(dtype):>10} {median_time*1e6:>12.2f} {std_time*1e6:>10.2f}")
+
+if __name__ == "__main__":
+    bench_scale()
+```
+
+**For more complex kernels**, consider:
+
+- Adding comparisons against reference implementations (e.g., PyTorch native, cuBLAS, cuDNN)
+- Using the unified benchmarking framework in `benchmarks/flashinfer_benchmark.py` if applicable
+- Testing across different problem sizes and configurations
+
+→ **For complete benchmarking guide, see [`.claude/skills/benchmark-kernel/SKILL.md`](../benchmark-kernel/SKILL.md)**
+
 ## Summary of Files Created/Modified
 
 ```
@@ -747,4 +801,5 @@ flashinfer/scale.py                        # NEW: Python API
 flashinfer/__init__.py                     # MODIFIED: Export API
 flashinfer/aot.py                          # MODIFIED: Register AOT
 tests/test_scale.py                        # NEW: Unit tests
+benchmarks/bench_scale.py                  # NEW: Benchmark script
 ```
diff --git a/.claude/skills/benchmark-kernel/SKILL.md b/.claude/skills/benchmark-kernel/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: benchmark-kernel
+description: Guide for benchmarking FlashInfer kernels with CUPTI timing
+---
+
 # Tutorial: Benchmarking FlashInfer Kernels
 
 This tutorial shows you how to accurately benchmark FlashInfer kernels.
diff --git a/.claude/skills/debug-cuda-crash/SKILL.md b/.claude/skills/debug-cuda-crash/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: debug-cuda-crash
+description: Tutorial for debugging CUDA crashes using API logging
+---
+
 # Tutorial: Debugging CUDA Crashes with API Logging
 
 This tutorial shows you how to debug CUDA crashes and errors in FlashInfer using the `@flashinfer_api` logging decorator.
PATCH

echo "Gold patch applied."
