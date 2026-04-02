#!/usr/bin/env bash
set -euo pipefail
cd /workspace/pytorch

# Idempotency check: if the new two-arg deleter signature already exists, skip
if grep -q 'void \*deleter_ctx' torch/csrc/stable/c/shim.h 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/torch/csrc/shim_common.cpp b/torch/csrc/shim_common.cpp
index d6c3cd2b41e0d..eac8147a30b29 100644
--- a/torch/csrc/shim_common.cpp
+++ b/torch/csrc/shim_common.cpp
@@ -667,7 +667,8 @@ AOTI_TORCH_EXPORT AOTITorchError torch_from_blob(
     int32_t layout,
     const uint8_t* opaque_metadata,
     int64_t opaque_metadata_size,
-    void (*deleter)(void*)) {
+    void (*deleter_callback)(void* data, void* ctx),
+    void* deleter_ctx) {
   AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE({
     c10::IntArrayRef sizes(sizes_ptr, ndim);
     c10::IntArrayRef strides(strides_ptr, ndim);
@@ -676,11 +677,14 @@ AOTI_TORCH_EXPORT AOTITorchError torch_from_blob(
         static_cast<c10::ScalarType>(dtype));
     at::Tensor tensor;
     if (data != nullptr) {
-      if (deleter != nullptr) {
+      if (deleter_callback != nullptr) {
+        auto wrapped_deleter = [deleter_callback, deleter_ctx](void* data) {
+          deleter_callback(data, deleter_ctx);
+        };
         tensor = at::for_blob(data, sizes)
                      .strides(strides)
                      .storage_offset(storage_offset)
-                     .deleter(deleter)
+                     .deleter(wrapped_deleter)
                      .options(options)
                      .make_tensor();
       } else {
diff --git a/torch/csrc/stable/c/shim.h b/torch/csrc/stable/c/shim.h
index f8a21e6c570f6..ec3caec593beb 100644
--- a/torch/csrc/stable/c/shim.h
+++ b/torch/csrc/stable/c/shim.h
@@ -165,8 +165,9 @@ AOTI_TORCH_EXPORT int32_t torch_dtype_float8_e8m0fnu();
 AOTI_TORCH_EXPORT int32_t torch_dtype_float4_e2m1fn_x2();

 // Creates a tensor from an existing data blob with an optional deleter.
-// The deleter is called with the data pointer when the tensor's storage
-// is deallocated.
+// The deleter receives both the data pointer and a caller-supplied context
+// pointer, which allows passing capturing lambdas across the C ABI boundary
+// by heap-allocating the callable and passing it as deleter_ctx.
 AOTI_TORCH_EXPORT AOTITorchError torch_from_blob(
     void* data,
     int64_t ndim,
@@ -180,7 +181,8 @@ AOTI_TORCH_EXPORT AOTITorchError torch_from_blob(
     int32_t layout,
     const uint8_t* opaque_metadata,
     int64_t opaque_metadata_size,
-    void (*deleter)(void*));
+    void (*deleter)(void* data, void* ctx),
+    void* deleter_ctx);

 #endif // TORCH_FEATURE_VERSION >= TORCH_VERSION_2_11_0

diff --git a/torch/csrc/stable/ops.h b/torch/csrc/stable/ops.h
index 19c109404cb5b..dbede4faba49e 100644
--- a/torch/csrc/stable/ops.h
+++ b/torch/csrc/stable/ops.h
@@ -5,6 +5,7 @@
 #include <cstdint>
 #include <optional>
 #include <string>
+#include <type_traits>

 #include <torch/csrc/inductor/aoti_torch/generated/c_shim_aten.h>
 #include <torch/csrc/stable/c/shim.h>
@@ -722,26 +723,28 @@ inline torch::stable::Tensor from_blob(
 ///
 /// This is the same as the from_blob function above, but allows specifying a
 /// custom deleter function that will be called when the tensor's storage is
-/// deallocated.
+/// deallocated. Accepts both plain function pointers and capturing lambdas.
+///
 /// Minimum compatible version: PyTorch 2.11.
 ///
+/// @tparam F The callable type. Must be invocable with (void*).
 /// @param data Pointer to the data buffer.
 /// @param sizes The size of each dimension of the tensor.
 /// @param strides The stride for each dimension.
 /// @param device The device where the data resides.
 /// @param dtype The scalar type of the data.
-/// @param deleter Function to call when the tensor is deallocated. May be
-///                nullptr if no cleanup is needed.
+/// @param deleter Callable to invoke when the tensor is deallocated.
 /// @param storage_offset The offset into the data buffer. Defaults to 0.
 /// @param layout The memory layout. Defaults to Strided.
 /// @return A tensor backed by the provided data.
+template <class F, std::enable_if_t<std::is_invocable_v<F, void*>, int> = 0>
 inline torch::stable::Tensor from_blob(
     void* data,
     torch::headeronly::IntHeaderOnlyArrayRef sizes,
     torch::headeronly::IntHeaderOnlyArrayRef strides,
     torch::stable::Device device,
     torch::headeronly::ScalarType dtype,
-    DeleterFnPtr deleter,
+    F deleter,
     int64_t storage_offset = 0,
     torch::headeronly::Layout layout = torch::headeronly::Layout::Strided) {
   auto shim_dtype =
@@ -750,21 +753,53 @@ inline torch::stable::Tensor from_blob(
       torch::stable::detail::from(device.type()));
   auto shim_layout =
       torch::stable::detail::to<int32_t>(torch::stable::detail::from(layout));
+
   AtenTensorHandle ath;
-  TORCH_ERROR_CODE_CHECK(torch_from_blob(
-      data,
-      sizes.size(),
-      sizes.data(),
-      strides.data(),
-      storage_offset,
-      shim_dtype,
-      shim_device_type,
-      device.index(),
-      &ath,
-      shim_layout,
-      nullptr,
-      0,
-      deleter));
+  if constexpr (std::is_convertible_v<F, DeleterFnPtr>) {
+    // Simple function pointer: pass it as ctx, no heap allocation.
+    auto deleter_callback = [](void* data, void* ctx) {
+      auto fn = reinterpret_cast<DeleterFnPtr>(ctx);
+      fn(data);
+    };
+    TORCH_ERROR_CODE_CHECK(torch_from_blob(
+        data,
+        sizes.size(),
+        sizes.data(),
+        strides.data(),
+        storage_offset,
+        shim_dtype,
+        shim_device_type,
+        device.index(),
+        &ath,
+        shim_layout,
+        nullptr,
+        0,
+        deleter_callback,
+        reinterpret_cast<void*>(static_cast<DeleterFnPtr>(deleter))));
+  } else {
+    // Capturing lambda: heap-allocate and type-erase.
+    F* heap_allocated_deleter = new F(std::move(deleter));
+    auto deleter_callback = [](void* data, void* ctx) {
+      F* func = static_cast<F*>(ctx);
+      (*func)(data);
+      delete func;
+    };
+    TORCH_ERROR_CODE_CHECK(torch_from_blob(
+        data,
+        sizes.size(),
+        sizes.data(),
+        strides.data(),
+        storage_offset,
+        shim_dtype,
+        shim_device_type,
+        device.index(),
+        &ath,
+        shim_layout,
+        nullptr,
+        0,
+        deleter_callback,
+        static_cast<void*>(heap_allocated_deleter)));
+  }
   return torch::stable::Tensor(ath);
 }
 #endif // TORCH_FEATURE_VERSION >= TORCH_VERSION_2_11_0

PATCH
