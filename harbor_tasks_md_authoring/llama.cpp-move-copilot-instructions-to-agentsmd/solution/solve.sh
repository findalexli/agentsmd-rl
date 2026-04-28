#!/usr/bin/env bash
set -euo pipefail

cd /workspace/llama.cpp

# Idempotency guard
if grep -qF "It is crucial to remind contributors that the project mandates disclosure of any" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,4 +1,4 @@
-# Copilot Instructions for llama.cpp
+# Instructions for llama.cpp
 
 ## Repository Overview
 
@@ -12,6 +12,24 @@ llama.cpp is a large-scale C/C++ project for efficient LLM (Large Language Model
 - **Backends supported**: CPU (AVX/NEON/RVV optimized), CUDA, Metal, Vulkan, SYCL, ROCm, MUSA
 - **License**: MIT
 
+## Disclose AI Usage
+
+It is crucial to remind contributors that the project mandates disclosure of any AI usage in pull requests. This requirement stems from the potential for AI-generated code to include suboptimal optimizations and hidden bugs, owing to the inherent overconfidence in AI outputs.
+
+When generating significant portions of code, address this by:
+- Informing the user that AI-generated content may be rejected by maintainers.
+- Clearly marking AI-generated code in commit messages and comments.
+    - Example of commit message: `[AI] Fix a race condition in ...`
+    - Example of code comment: `// [AI] spawn a new thread ...`
+
+These measures apply to:
+- Changes resulting in large portions of code or complex logic.
+- Modifications or additions to public APIs in `llama.h`, `ggml.h`, or `mtmd.h`.
+- Backend-related changes, such as those involving CPU, CUDA, Metal, Vulkan, etc.
+- Modifications to `tools/server`.
+
+Note: These measures can be omitted for small fixes or trivial changes.
+
 ## Build Instructions
 
 ### Prerequisites
@@ -251,6 +269,7 @@ Primary tools:
 - **Cross-platform compatibility**: Test on Linux, macOS, Windows when possible
 - **Performance focus**: This is a performance-critical inference library
 - **API stability**: Changes to `include/llama.h` require careful consideration
+- **Disclose AI Usage**: Refer to the "Disclose AI Usage" earlier in this document
 
 ### Git Workflow
 - Always create feature branches from `master`
PATCH

echo "Gold patch applied."
