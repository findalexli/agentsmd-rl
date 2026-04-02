#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency: check if fix is already applied (old GIT_TAG present)
if grep -q 'be055fb7df0090fde45f08e9cb5b8b4c0272da73' sgl-kernel/cmake/flashmla.cmake 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

# Remove _flashmla_import_error guards from all 3 Python functions
python3 -c "
import re
with open('sgl-kernel/python/sgl_kernel/flash_mla.py') as f:
    content = f.read()
# Remove the guard lines (2 lines: if check + raise)
content = re.sub(r'\n    if _flashmla_import_error is not None:\n        raise _IMPORT_ERROR from _flashmla_import_error\n', '\n', content)
with open('sgl-kernel/python/sgl_kernel/flash_mla.py', 'w') as f:
    f.write(content)
print('Python import guards removed.')
"

git apply - <<'PATCH'
diff --git a/sgl-kernel/cmake/flashmla.cmake b/sgl-kernel/cmake/flashmla.cmake
index d52aadf3f082..b1546b151020 100644
--- a/sgl-kernel/cmake/flashmla.cmake
+++ b/sgl-kernel/cmake/flashmla.cmake
@@ -4,7 +4,7 @@ include(FetchContent)
 FetchContent_Declare(
     repo-flashmla
     GIT_REPOSITORY https://github.com/sgl-project/FlashMLA
-    GIT_TAG 9804b12079e4c873514d3457aa588d3ccf40da28
+    GIT_TAG be055fb7df0090fde45f08e9cb5b8b4c0272da73
     GIT_SHALLOW OFF
 )
 FetchContent_Populate(repo-flashmla)
@@ -34,9 +34,8 @@ if(${CUDA_VERSION} VERSION_GREATER_EQUAL "13.0")
     # Patch FlashMLA sources for SM103a support.
     # These patches are only needed (and only valid) with CUDA 13+.

-    # Patch utils.h: widen IS_SM100 to cover the full SM100 family.
-    # Newer FlashMLA versions use csrc/utils.h.
-    set(FLASHMLA_UTILS_FILE "${repo-flashmla_SOURCE_DIR}/csrc/utils.h")
+    # Patch flashmla_utils.h: widen IS_SM100 to cover the full SM100 family
+    set(FLASHMLA_UTILS_FILE "${repo-flashmla_SOURCE_DIR}/csrc/flashmla_utils.h")
     file(READ "${FLASHMLA_UTILS_FILE}" FLASHMLA_UTILS_CONTENT)
     string(REPLACE
         "#if defined(__CUDA_ARCH__) && (__CUDA_ARCH__ == 1000)
@@ -45,7 +44,7 @@ if(${CUDA_VERSION} VERSION_GREATER_EQUAL "13.0")
 #define IS_SM100 1"
         FLASHMLA_UTILS_CONTENT "${FLASHMLA_UTILS_CONTENT}")
     file(WRITE "${FLASHMLA_UTILS_FILE}" "${FLASHMLA_UTILS_CONTENT}")
-    message(STATUS "Patched utils.h for SM103a support")
+    message(STATUS "Patched flashmla_utils.h for SM103a support")

     # Patch cutlass/arch/config.h: add SM103 architecture defines.
     # The new block is inserted right before the existing "// SM101 and SM101a"
@@ -88,46 +87,16 @@ endif()

 set(FlashMLA_SOURCES
     "csrc/flashmla_extension.cc"
-
-    # Compatibility shim for sgl-kernel torch.ops API.
     ${repo-flashmla_SOURCE_DIR}/csrc/python_api.cpp
-
-    # Decode metadata/combine kernels.
-    ${repo-flashmla_SOURCE_DIR}/csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/smxx/decode/combine/combine.cu
-
-    # sm90 dense decode.
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/dense/instantiations/fp16.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/dense/instantiations/bf16.cu
-
-    # sm90 sparse decode.
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/sparse_fp8/instantiations/model1_persistent_h64.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/sparse_fp8/instantiations/model1_persistent_h128.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/sparse_fp8/instantiations/v32_persistent_h64.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/sparse_fp8/instantiations/v32_persistent_h128.cu
-
-    # sm90 sparse prefill.
+    ${repo-flashmla_SOURCE_DIR}/csrc/smxx/get_mla_metadata.cu
+    ${repo-flashmla_SOURCE_DIR}/csrc/smxx/mla_combine.cu
+    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/dense/splitkv_mla.cu
+    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/decode/sparse_fp8/splitkv_mla.cu
     ${repo-flashmla_SOURCE_DIR}/csrc/sm90/prefill/sparse/fwd.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/prefill/sparse/instantiations/phase1_k512.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/prefill/sparse/instantiations/phase1_k512_topklen.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/prefill/sparse/instantiations/phase1_k576.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm90/prefill/sparse/instantiations/phase1_k576_topklen.cu
-
-    # sm100 dense prefill/bwd.
+    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/decode/sparse_fp8/splitkv_mla.cu
     ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/dense/fmha_cutlass_fwd_sm100.cu
     ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/dense/fmha_cutlass_bwd_sm100.cu
-
-    # sm100 sparse prefill.
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd/head64/instantiations/phase1_k512.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd/head64/instantiations/phase1_k576.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd/head128/instantiations/phase1_k512.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd/head128/instantiations/phase1_k576.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd_for_small_topk/head128/instantiations/phase1_prefill_k512.cu
-
-    # sm100 sparse decode.
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/decode/head64/instantiations/v32.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/decode/head64/instantiations/model1.cu
-    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd_for_small_topk/head128/instantiations/phase1_decode_k512.cu
+    ${repo-flashmla_SOURCE_DIR}/csrc/sm100/prefill/sparse/fwd.cu

     ${repo-flashmla_SOURCE_DIR}/csrc/extension/sm90/dense_fp8/dense_fp8_python_api.cpp
     ${repo-flashmla_SOURCE_DIR}/csrc/extension/sm90/dense_fp8/flash_fwd_mla_fp8_sm90.cu
@@ -135,14 +104,9 @@ set(FlashMLA_SOURCES
 )

 Python_add_library(flashmla_ops MODULE USE_SABI ${SKBUILD_SABI_VERSION} WITH_SOABI ${FlashMLA_SOURCES})
-target_compile_options(flashmla_ops PRIVATE
-    $<$<COMPILE_LANGUAGE:CXX>:-std=c++20>
-    $<$<COMPILE_LANGUAGE:CUDA>:-std=c++20>
-    $<$<COMPILE_LANGUAGE:CUDA>:${FLASHMLA_CUDA_FLAGS}>
-)
+target_compile_options(flashmla_ops PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:${FLASHMLA_CUDA_FLAGS}>)
 target_include_directories(flashmla_ops PRIVATE
     ${repo-flashmla_SOURCE_DIR}/csrc
-    ${repo-flashmla_SOURCE_DIR}/csrc/kerutils/include
     ${repo-flashmla_SOURCE_DIR}/csrc/sm90
     ${repo-flashmla_SOURCE_DIR}/csrc/extension/sm90/dense_fp8/
     ${repo-flashmla_SOURCE_DIR}/csrc/cutlass/include

PATCH

echo "Patch applied successfully."
