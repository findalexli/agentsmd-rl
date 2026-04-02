#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pytorch

TARGET="torch/utils/cpp_extension.py"

# Idempotency check: look for the filter function
if grep -q 'win_filter_msvc_include_dirs' "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/torch/utils/cpp_extension.py b/torch/utils/cpp_extension.py
index a63bff50d5ec3..109a6608aa4bd 100644
--- a/torch/utils/cpp_extension.py
+++ b/torch/utils/cpp_extension.py
@@ -947,6 +947,20 @@ def win_cuda_flags(cflags):
         def win_hip_flags(cflags):
             return (COMMON_HIPCC_FLAGS + COMMON_HIP_FLAGS + cflags + _get_rocm_arch_flags(cflags))

+        def win_filter_msvc_include_dirs(pp_opts) -> list[str]:
+            """Filter out MSVC include dirs from pp_opts for oneAPI 2025.3+."""
+            # oneAPI 2025.3+ changed include path ordering to match MSVC behavior.
+            # Filter out MSVC headers to avoid conflicting declarations with oneAPI's std headers.
+            icpx_version = int(_get_icpx_version())
+            if icpx_version >= 20250300:
+                vc_tools_dir = os.path.normcase(os.environ.get('VCToolsInstallDir', ''))
+                if vc_tools_dir:
+                    pp_opts = [
+                        path for path in pp_opts
+                        if vc_tools_dir not in os.path.normcase(path)
+                    ]
+            return pp_opts
+
         def win_wrap_single_compile(sources,
                                     output_dir=None,
                                     macros=None,
@@ -1116,7 +1130,7 @@ def win_wrap_ninja_compile(sources,
             sycl_post_cflags = None
             sycl_dlink_post_cflags = None
             if with_sycl:
-                sycl_cflags = common_cflags + pp_opts + _COMMON_SYCL_FLAGS
+                sycl_cflags = common_cflags + win_filter_msvc_include_dirs(pp_opts) + _COMMON_SYCL_FLAGS
                 if isinstance(extra_postargs, dict):
                     sycl_post_cflags = extra_postargs['sycl']
                 else:

PATCH

echo "Patch applied successfully."
