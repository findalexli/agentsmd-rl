#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q 'CUDA_VERSION >= 13000' csrc/cache_kernels.cu 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/csrc/cache_kernels.cu b/csrc/cache_kernels.cu
index c59da4379daf..a7e5fdabf648 100644
--- a/csrc/cache_kernels.cu
+++ b/csrc/cache_kernels.cu
@@ -91,9 +91,9 @@ void swap_blocks_batch(const torch::Tensor& src_ptrs,

   if (n == 0) return;

-  const int64_t* src_data = src_ptrs.data_ptr<int64_t>();
-  const int64_t* dst_data = dst_ptrs.data_ptr<int64_t>();
-  const int64_t* size_data = sizes.data_ptr<int64_t>();
+  int64_t* src_data = src_ptrs.mutable_data_ptr<int64_t>();
+  int64_t* dst_data = dst_ptrs.mutable_data_ptr<int64_t>();
+  int64_t* size_data = sizes.mutable_data_ptr<int64_t>();

   const cudaStream_t stream = at::cuda::getCurrentCUDAStream();

@@ -107,15 +107,24 @@ void swap_blocks_batch(const torch::Tensor& src_ptrs,
   CUmemcpyAttributes attr = {};
   attr.srcAccessOrder = CU_MEMCPY_SRC_ACCESS_ORDER_STREAM;
   size_t attrs_idx = 0;
+  #if defined(CUDA_VERSION) && CUDA_VERSION >= 13000
+  CUresult result = cuMemcpyBatchAsync(
+      reinterpret_cast<CUdeviceptr*>(dst_data),
+      reinterpret_cast<CUdeviceptr*>(src_data),
+      reinterpret_cast<size_t*>(size_data), static_cast<size_t>(n), &attr,
+      &attrs_idx, 1, static_cast<CUstream>(stream));
+  TORCH_CHECK(result == CUDA_SUCCESS, "cuMemcpyBatchAsync failed with error ",
+              result);
+  #else
   size_t fail_idx = 0;
   CUresult result = cuMemcpyBatchAsync(
-      reinterpret_cast<CUdeviceptr*>(const_cast<int64_t*>(dst_data)),
-      reinterpret_cast<CUdeviceptr*>(const_cast<int64_t*>(src_data)),
-      reinterpret_cast<size_t*>(const_cast<int64_t*>(size_data)),
-      static_cast<size_t>(n), &attr, &attrs_idx, 1, &fail_idx,
-      static_cast<CUstream>(stream));
+      reinterpret_cast<CUdeviceptr*>(dst_data),
+      reinterpret_cast<CUdeviceptr*>(src_data),
+      reinterpret_cast<size_t*>(size_data), static_cast<size_t>(n), &attr,
+      &attrs_idx, 1, &fail_idx, static_cast<CUstream>(stream));
   TORCH_CHECK(result == CUDA_SUCCESS, "cuMemcpyBatchAsync failed at index ",
               fail_idx, " with error ", result);
+  #endif
 #else
   // Fallback for CUDA < 12.8 and ROCm: individual async copies.
   // cudaMemcpyDefault lets the driver infer direction from pointer types.

PATCH

echo "Patch applied successfully."
