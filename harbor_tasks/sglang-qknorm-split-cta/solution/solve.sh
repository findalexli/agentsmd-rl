#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

TARGET="python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"

# Idempotency: check if fix is already applied (split CTA uses blockIdx.y)
if grep -q 'blockIdx\.y' "$TARGET" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh b/python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh
index 9286d79322b2..39630cdae6ea 100644
--- a/python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh
+++ b/python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh
@@ -42,7 +42,7 @@ struct VecTypeTrait<fp16_t, 32> {
 };

 template <typename packed_t>
-SGL_DEVICE packed_t rms(packed_t& val, packed_t& weight, float rsqrt_square_sum) {
+SGL_DEVICE packed_t rms(const packed_t& val, const packed_t& weight, float rsqrt_square_sum) {
   float2 valf = device::cast<fp32x2_t, packed_t>(val);
   float2 weightf = device::cast<fp32x2_t, packed_t>(weight);
   return device::cast<packed_t, fp32x2_t>(
@@ -59,104 +59,56 @@ __global__ void qknorm_across_heads_reg_kernel(
     float eps) {
   constexpr int inner_loop = VEC_SIZE_IN_BYTE == 16 ? 4 : 8;

-  __shared__ float shared_memory[64];  // Used for CTA reduce, store both Q and K rsqrt
+  __shared__ float shared_memory[32];

   using vec_t = typename VecTypeTrait<T, VEC_SIZE_IN_BYTE>::vec_t;
   using packed_t = typename VecTypeTrait<T, VEC_SIZE_IN_BYTE>::packed_t;
-  vec_t v_q;         // Save q
-  vec_t v_k;         // Save k
-  vec_t v_q_weight;  // Save q_weight
-  vec_t v_k_weight;  // Save k_weight
-  vec_t v_q_out;     // Save q output
-  vec_t v_k_out;     // Save k output
-
-  auto token_id = blockIdx.x;
-  float2 acc_square_q = make_float2(0.0f, 0.0f);  // Sum of squares for q
-  float2 acc_square_k = make_float2(0.0f, 0.0f);  // Sum of squares for k
+  vec_t v_data;
+  vec_t v_weight;
+  const int warp_id = threadIdx.x >> 5;
+  const int lane_id = threadIdx.x & 31;
+  const int warp_count = (blockDim.x + 31) >> 5;
+  const float inv_hidden_size = 1.0f / static_cast<float>(vec_hidden_size * (VEC_SIZE_IN_BYTE / sizeof(T)));
+  const bool is_q = blockIdx.y == 0;
+
+  const auto token_id = blockIdx.x;
+  float2 acc_square = make_float2(0.0f, 0.0f);
+  vec_t* data = reinterpret_cast<vec_t*>(is_q ? q : k) + token_id * vec_hidden_size;
+  const vec_t* weight = reinterpret_cast<const vec_t*>(is_q ? q_weight : k_weight);

   if (threadIdx.x < vec_hidden_size) {
-    // Compute address for q and k
-    vec_t* p_q = reinterpret_cast<vec_t*>(q) + token_id * vec_hidden_size;
-    vec_t* p_k = reinterpret_cast<vec_t*>(k) + token_id * vec_hidden_size;
-    const vec_t* p_q_weight = reinterpret_cast<const vec_t*>(q_weight);
-    const vec_t* p_k_weight = reinterpret_cast<const vec_t*>(k_weight);
-
-    // Load data
-    v_q = p_q[threadIdx.x];
-    v_k = p_k[threadIdx.x];
-    v_q_weight = p_q_weight[threadIdx.x];
-    v_k_weight = p_k_weight[threadIdx.x];
-
-    // Compute sum of squares for q
-    for (int i = 0; i < inner_loop; i++) {
-      float2 val = device::cast<fp32x2_t, packed_t>(v_q[i]);
-      acc_square_q.x += val.x * val.x;
-      acc_square_q.y += val.y * val.y;
-    }
-
-    // Compute sum of squares for k
+    v_data = data[threadIdx.x];
+    v_weight = weight[threadIdx.x];
     for (int i = 0; i < inner_loop; i++) {
-      float2 val = device::cast<fp32x2_t, packed_t>(v_k[i]);
-      acc_square_k.x += val.x * val.x;
-      acc_square_k.y += val.y * val.y;
+      float2 val = device::cast<fp32x2_t, packed_t>(v_data[i]);
+      acc_square.x += val.x * val.x;
+      acc_square.y += val.y * val.y;
     }
   }

   auto cg_warp = cooperative_groups::tiled_partition<32>(cooperative_groups::this_thread_block());
-  float* buffer_q = shared_memory;       // [0, 31] for Q
-  float* buffer_k = shared_memory + 32;  // [32, 63] for K
-
-  // ========== Reduction phase: Compute rsqrt for both Q and K ==========
-
-  // Step 0: Warp Reduce for Q
-  float warp_sum_q =
-      cooperative_groups::reduce(cg_warp, acc_square_q.x + acc_square_q.y, cooperative_groups::plus<float>());
-  if (threadIdx.x % 32 == 0) {
-    buffer_q[threadIdx.x / 32] = warp_sum_q;
+  float* buffer = shared_memory;
+  float warp_sum = cooperative_groups::reduce(cg_warp, acc_square.x + acc_square.y, cooperative_groups::plus<float>());
+  if (lane_id == 0) {
+    buffer[warp_id] = warp_sum;
   }

-  // Step 0: Warp Reduce for K
-  float warp_sum_k =
-      cooperative_groups::reduce(cg_warp, acc_square_k.x + acc_square_k.y, cooperative_groups::plus<float>());
-  if (threadIdx.x % 32 == 0) {
-    buffer_k[threadIdx.x / 32] = warp_sum_k;
-  }
-
-  // Step 1: CTA Reduce for both Q and K
   __syncthreads();
   if (threadIdx.x < 32) {
-    // CTA Reduce for Q
-    float cta_sum_q = cooperative_groups::reduce(
-        cg_warp, (threadIdx.x < blockDim.x / 32) ? buffer_q[threadIdx.x] : 0.0f, cooperative_groups::plus<float>());
-    buffer_q[threadIdx.x] =
-        rsqrtf(eps + cta_sum_q * (1.0f / static_cast<float>(vec_hidden_size * (VEC_SIZE_IN_BYTE / sizeof(T)))));
-
-    // CTA Reduce for K
-    float cta_sum_k = cooperative_groups::reduce(
-        cg_warp, (threadIdx.x < blockDim.x / 32) ? buffer_k[threadIdx.x] : 0.0f, cooperative_groups::plus<float>());
-    buffer_k[threadIdx.x] =
-        rsqrtf(eps + cta_sum_k * (1.0f / static_cast<float>(vec_hidden_size * (VEC_SIZE_IN_BYTE / sizeof(T)))));
+    float cta_sum = cooperative_groups::reduce(
+        cg_warp, (threadIdx.x < warp_count) ? buffer[threadIdx.x] : 0.0f, cooperative_groups::plus<float>());
+    if (threadIdx.x == 0) {
+      buffer[0] = rsqrtf(eps + cta_sum * inv_hidden_size);
+    }
   }
   __syncthreads();

-  // ========== Apply normalization phase: Compute and write back Q and K ==========
-
   if (threadIdx.x < vec_hidden_size) {
-    // Apply RMSNorm for Q
-    float rsqrt_q = buffer_q[threadIdx.x / 32];
-    for (int i = 0; i < inner_loop; i++) {
-      v_q_out[i] = rms(v_q[i], v_q_weight[i], rsqrt_q);
-    }
-    vec_t* p_q_out = reinterpret_cast<vec_t*>(q) + token_id * vec_hidden_size;
-    p_q_out[threadIdx.x] = v_q_out;
-
-    // Apply RMSNorm for K
-    float rsqrt_k = buffer_k[threadIdx.x / 32];
+    float rsqrt_val = buffer[0];
     for (int i = 0; i < inner_loop; i++) {
-      v_k_out[i] = rms(v_k[i], v_k_weight[i], rsqrt_k);
+      v_data[i] = rms(v_data[i], v_weight[i], rsqrt_val);
     }
-    vec_t* p_k_out = reinterpret_cast<vec_t*>(k) + token_id * vec_hidden_size;
-    p_k_out[threadIdx.x] = v_k_out;
+    data[threadIdx.x] = v_data;
   }
 }

@@ -207,10 +159,9 @@ struct QKNormAcrossHeadsKernel {
           " can not align to elements_in_vec ",
           elements_in_vec);

-      // Launch single kernel for both q and k
       auto kernel = qknorm_across_heads_reg_kernel<DType, device::kMaxVecBytes>;

-      LaunchKernel(static_cast<uint>(N.unwrap()), threads, device.unwrap())
+      LaunchKernel(dim3(static_cast<uint>(N.unwrap()), 2), threads, device.unwrap())
           .enable_pdl(false)(
               kernel,
               reinterpret_cast<DType*>(q.data_ptr()),

PATCH

echo "Patch applied successfully."
