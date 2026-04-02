#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Idempotent: check if patch is already applied
if grep -q 'triton_available' src/transformers/quantizers/quantizer_mxfp4.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn - <<'PATCH'
diff --git a/src/transformers/quantizers/quantizer_mxfp4.py b/src/transformers/quantizers/quantizer_mxfp4.py
index a0755fa68c61..7859a8ff739a 100644
--- a/src/transformers/quantizers/quantizer_mxfp4.py
+++ b/src/transformers/quantizers/quantizer_mxfp4.py
@@ -90,44 +90,61 @@ def validate_environment(self, *args, **kwargs):

         if torch.xpu.is_available():
             is_device_supported_mxfp4 = True
-            kernels_available = is_triton_available("3.5.0") and is_kernels_available()
+            triton_available = is_triton_available("3.5.0")
+            kernels_installed = is_kernels_available()
         elif torch.cuda.is_available():
             compute_capability = torch.cuda.get_device_capability()
             is_device_supported_mxfp4 = compute_capability >= (7, 5)
-            kernels_available = is_triton_available("3.4.0") and is_kernels_available()
+            triton_available = is_triton_available("3.4.0")
+            kernels_installed = is_kernels_available()
         elif device.type == "cpu":
             is_device_supported_mxfp4 = True
-            kernels_available = is_triton_available("3.5.0") and is_kernels_available()
+            triton_available = is_triton_available("3.5.0")
+            kernels_installed = is_kernels_available()
         else:
             is_device_supported_mxfp4 = False
-            kernels_available = False
+            triton_available = False
+            kernels_installed = False

         if self.pre_quantized:
-            # On unsupported GPUs or without kernels, we will dequantize the model to bf16
             if not is_device_supported_mxfp4:
                 logger.warning_once(
-                    "MXFP4 quantization is only supported on GPUs with compute capability >= 7.5 (e.g T4, A100, L4, H100, or B200) or XPUs (e.g Intel\u00ae Data Center GPU Max Series) "
+                    "MXFP4 quantization is only supported on GPUs with compute capability >= 7.5 "
+                    "(e.g T4, A100, L4, H100, or B200) or XPUs (e.g Intel\u00ae Data Center GPU Max Series). "
                     "We will default to dequantizing the model to bf16."
                 )
                 self.quantization_config.dequantize = True
                 return

-            if not kernels_available:
+            if not triton_available:
                 logger.warning_once(
-                    "MXFP4 quantization requires Triton and kernels installed: CUDA requires Triton >= 3.4.0, XPU requires Triton >= 3.5.0, we will default to dequantizing the model to bf16"
+                    "MXFP4 quantization requires Triton: CUDA requires Triton >= 3.4.0, "
+                    "XPU/CPU requires Triton >= 3.5.0. Please install triton: `pip install triton`. "
+                    "We will default to dequantizing the model to bf16."
+                )
+                self.quantization_config.dequantize = True
+                return
+
+            if not kernels_installed:
+                logger.warning_once(
+                    "MXFP4 quantization requires the `kernels` package: "
+                    "`pip install kernels>=0.12.0`. "
+                    "We will default to dequantizing the model to bf16."
                 )
                 self.quantization_config.dequantize = True
                 return
         elif not is_device_supported_mxfp4:
-            # we can't quantize the model in this case so we raise an error
             raise ValueError(
-                "MXFP4 quantization is only supported on GPUs with compute capability >= 7.5 (e.g T4, A100, L4, H100, or B200) or XPUs (e.g Intel\u00ae Data Center GPU Max Series) or CPU"
+                "MXFP4 quantization is only supported on GPUs with compute capability >= 7.5 "
+                "(e.g T4, A100, L4, H100, or B200) or XPUs (e.g Intel\u00ae Data Center GPU Max Series) or CPU"
             )
-        elif not kernels_available:
-            # we can't quantize the model in this case so we raise an error
+        elif not triton_available:
             raise ValueError(
-                "MXFP4 quantization requires Triton and kernels installed: CUDA requires Triton >= 3.4.0, XPU/CPU requires Triton >= 3.5.0"
+                "MXFP4 quantization requires Triton: CUDA requires Triton >= 3.4.0, "
+                "XPU/CPU requires Triton >= 3.5.0. Please install triton: `pip install triton`"
             )
+        elif not kernels_installed:
+            raise ValueError("MXFP4 quantization requires the `kernels` package: `pip install kernels>=0.12.0`")

         if not self.pre_quantized:
             self._lazy_import_kernels()

PATCH
