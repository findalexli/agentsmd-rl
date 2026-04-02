#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if registration already present, skip
if grep -q "register_cuda_ci" python/sglang/jit_kernel/benchmark/bench_cast.py 2>/dev/null && \
   grep -q "register_cuda_ci" python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py 2>/dev/null && \
   grep -q "register_cuda_ci" python/sglang/jit_kernel/tests/test_cast.py 2>/dev/null && \
   grep -q "register_cuda_ci" python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py 2>/dev/null; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/jit_kernel/benchmark/bench_cast.py b/python/sglang/jit_kernel/benchmark/bench_cast.py
index 18dbbf726f99..b4b5109569ac 100644
--- a/python/sglang/jit_kernel/benchmark/bench_cast.py
+++ b/python/sglang/jit_kernel/benchmark/bench_cast.py
@@ -9,6 +9,9 @@
     run_benchmark,
 )
 from sglang.jit_kernel.cast import downcast_fp8 as downcast_fp8_jit
+from sglang.test.ci.ci_register import register_cuda_ci
+
+register_cuda_ci(est_time=10, suite="stage-b-kernel-benchmark-1-gpu-large")

 DEVICE = DEFAULT_DEVICE
 DTYPE = torch.bfloat16
diff --git a/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py b/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py
index e6ef6bc77a36..8c120cd0f962 100644
--- a/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py
+++ b/python/sglang/jit_kernel/benchmark/bench_fused_qknorm_rope.py
@@ -18,6 +18,9 @@
 from sglang.jit_kernel.fused_qknorm_rope import (
     fused_qk_norm_rope as fused_qk_norm_rope_jit,
 )
+from sglang.test.ci.ci_register import register_cuda_ci
+
+register_cuda_ci(est_time=6, suite="stage-b-kernel-benchmark-1-gpu-large")

 try:
     from sgl_kernel import fused_qk_norm_rope as fused_qk_norm_rope_aot
diff --git a/python/sglang/jit_kernel/tests/test_cast.py b/python/sglang/jit_kernel/tests/test_cast.py
index 6a71dc194214..a63b4023c45f 100644
--- a/python/sglang/jit_kernel/tests/test_cast.py
+++ b/python/sglang/jit_kernel/tests/test_cast.py
@@ -2,6 +2,10 @@
 import torch

 from sglang.jit_kernel.cast import downcast_fp8
+from sglang.test.ci.ci_register import register_cuda_ci
+
+register_cuda_ci(est_time=15, suite="stage-b-kernel-unit-1-gpu-large")
+register_cuda_ci(est_time=120, suite="nightly-kernel-1-gpu", nightly=True)

 DTYPES = [torch.bfloat16, torch.float16]

diff --git a/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py b/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py
index 10c6572900d3..898683d15c3c 100644
--- a/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py
+++ b/python/sglang/jit_kernel/tests/test_fused_qknorm_rope.py
@@ -9,6 +9,10 @@
 import torch

 from sglang.jit_kernel.fused_qknorm_rope import fused_qk_norm_rope
+from sglang.test.ci.ci_register import register_cuda_ci
+
+register_cuda_ci(est_time=35, suite="stage-b-kernel-unit-1-gpu-large")
+register_cuda_ci(est_time=256, suite="nightly-kernel-1-gpu", nightly=True)

 try:
     from sgl_kernel import fused_qk_norm_rope as fused_qk_norm_rope_aot

PATCH

echo "Patch applied successfully."
