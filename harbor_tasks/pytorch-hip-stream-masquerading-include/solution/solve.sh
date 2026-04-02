#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

# Idempotency check: if getCurrentHIPStreamMasqueradingAsCUDA is already in CUDAStream.h, skip
if grep -q 'getCurrentHIPStreamMasqueradingAsCUDA' c10/cuda/CUDAStream.h; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h b/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h
index a6d24a55c7b0d..1c0047371d7b6 100644
--- a/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h
+++ b/aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h
@@ -24,33 +24,6 @@ class HIPStreamMasqueradingAsCUDA final : public c10::cuda::CUDAStream {
   c10::cuda::CUDAStream hip_stream() const { return *this; }
 };

-HIPStreamMasqueradingAsCUDA
-inline getStreamFromPoolMasqueradingAsCUDA(const bool isHighPriority = false, DeviceIndex device = -1) {
-  return HIPStreamMasqueradingAsCUDA(c10::cuda::getStreamFromPool(isHighPriority, device));
-}
-
-HIPStreamMasqueradingAsCUDA
-inline getStreamFromPoolMasqueradingAsCUDA(const int priority, DeviceIndex device = -1) {
-  return HIPStreamMasqueradingAsCUDA(c10::cuda::getStreamFromPool(priority, device));
-}
-
-HIPStreamMasqueradingAsCUDA
-inline getStreamFromExternalMasqueradingAsCUDA(hipStream_t ext_stream, DeviceIndex device) {
-  return HIPStreamMasqueradingAsCUDA(c10::cuda::getStreamFromExternal(ext_stream, device));
-}
-
-inline HIPStreamMasqueradingAsCUDA getDefaultHIPStreamMasqueradingAsCUDA(DeviceIndex device_index = -1) {
-  return HIPStreamMasqueradingAsCUDA(c10::cuda::getDefaultCUDAStream(device_index));
-}
-
-inline HIPStreamMasqueradingAsCUDA getCurrentHIPStreamMasqueradingAsCUDA(DeviceIndex device_index = -1) {
-  return HIPStreamMasqueradingAsCUDA(c10::cuda::getCurrentCUDAStream(device_index));
-}
-
-inline void setCurrentHIPStreamMasqueradingAsCUDA(HIPStreamMasqueradingAsCUDA stream) {
-  c10::cuda::setCurrentCUDAStream(stream.hip_stream());
-}
-
 inline std::ostream& operator<<(std::ostream& stream, const HIPStreamMasqueradingAsCUDA& s) {
   stream << s.hip_stream() << " (masquerading as CUDA)";
   return stream;
diff --git a/c10/cuda/CUDAStream.h b/c10/cuda/CUDAStream.h
index d3d1402593751..f27c7c9176631 100644
--- a/c10/cuda/CUDAStream.h
+++ b/c10/cuda/CUDAStream.h
@@ -256,6 +256,28 @@ inline c10::cuda::CUDAStream getCurrentHIPStream(
   return c10::cuda::getCurrentCUDAStream(device_index);
 }
 inline auto& setCurrentHIPStream = c10::cuda::setCurrentCUDAStream;
+inline c10::cuda::CUDAStream getStreamFromPoolMasqueradingAsCUDA(
+    const bool isHighPriority = false,
+    DeviceIndex device = -1) {
+  return c10::cuda::getStreamFromPool(isHighPriority, device);
+}
+inline c10::cuda::CUDAStream getStreamFromPoolMasqueradingAsCUDA(
+    const int priority,
+    DeviceIndex device = -1) {
+  return c10::cuda::getStreamFromPool(priority, device);
+}
+inline auto& getStreamFromExternalMasqueradingAsCUDA =
+    c10::cuda::getStreamFromExternal;
+inline c10::cuda::CUDAStream getDefaultHIPStreamMasqueradingAsCUDA(
+    DeviceIndex device_index = -1) {
+  return c10::cuda::getDefaultCUDAStream(device_index);
+}
+inline c10::cuda::CUDAStream getCurrentHIPStreamMasqueradingAsCUDA(
+    DeviceIndex device_index = -1) {
+  return c10::cuda::getCurrentCUDAStream(device_index);
+}
+inline auto& setCurrentHIPStreamMasqueradingAsCUDA =
+    c10::cuda::setCurrentCUDAStream;
 } // namespace c10::hip
 #endif

PATCH

echo "Patch applied successfully."
