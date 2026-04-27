#!/bin/bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency guard: distinctive line from the gold patch
if grep -q "fp8-inference" pyproject.toml 2>/dev/null && [ -f skills/installation/SKILL.md ]; then
    echo "Already applied"
    exit 0
fi

git apply <<'PATCH'
diff --git a/pyproject.toml b/pyproject.toml
index 0351a498cd..5e258d8b5a 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -58,8 +58,10 @@ flash-attn-3 = [
 flash-attn-cute = [
     "flash-attn-cute",
 ]
-
 [dependency-groups]
+fp8-inference = [
+    "deep-gemm @ https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl",
+]
 dev = [
     "ipykernel>=6.29.5",
     "ipywidgets>=8.1.7",
diff --git a/skills/installation/SKILL.md b/skills/installation/SKILL.md
new file mode 100644
index 0000000000..968501b5fe
--- /dev/null
+++ b/skills/installation/SKILL.md
@@ -0,0 +1,47 @@
+---
+name: installation
+description: How to install prime-rl and its optional dependencies. Use when setting up the project, installing extras like deep-gemm for FP8 models, or troubleshooting dependency issues.
+---
+
+# Installation
+
+## Basic install
+
+```bash
+uv sync
+```
+
+This installs all core dependencies defined in `pyproject.toml`.
+
+## All extras at once
+
+The recommended way to install for most users:
+
+```bash
+uv sync --all-extras
+```
+
+This installs all optional extras (flash-attn, flash-attn-cute, etc.) in one go.
+
+## FP8 inference with deep-gemm
+
+For certain models like GLM-5-FP8, you need `deep-gemm`. Install it via the `fp8-inference` dependency group:
+
+```bash
+uv sync --group fp8-inference
+```
+
+This installs the pre-built `deep-gemm` wheel. No CUDA build step is needed.
+
+## Dev dependencies
+
+```bash
+uv sync --group dev
+```
+
+Installs pytest, ruff, pre-commit, and other development tools.
+
+## Key files
+
+- `pyproject.toml` — all dependencies, extras, and dependency groups
+- `uv.lock` — pinned lockfile (update with `uv sync --all-extras`)
diff --git a/uv.lock b/uv.lock
index 30f28ab72f..304b751ae4 100644
--- a/uv.lock
+++ b/uv.lock
@@ -562,6 +562,14 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/4e/8c/f3147f5c4b73e7550fe5f9352eaa956ae838d5c51eb58e7a25b9f3e2643b/decorator-5.2.1-py3-none-any.whl", hash = "sha256:d316bb415a2d9e2d2b3abcc4084c6502fc09240e292cd76a76afc106a1c8e04a", size = 9190, upload-time = "2025-02-24T04:41:32.565Z" },
 ]

+[[package]]
+name = "deep-gemm"
+version = "2.3.0+35c4bc8"
+source = { url = "https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl" }
+wheels = [
+    { url = "https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl", hash = "sha256:e335e99dffeee5a10e91f375d3e9a8ed348f144ffa56aebff1576b9a2b56b697" },
+]
+
 [[package]]
 name = "depyf"
 version = "0.20.0"
@@ -2361,6 +2369,9 @@ dev = [
     { name = "pytest" },
     { name = "ruff" },
 ]
+fp8-inference = [
+    { name = "deep-gemm" },
+]

 [package.metadata]
 requires-dist = [
@@ -2408,6 +2419,7 @@ dev = [
     { name = "pytest", specifier = ">=8.4.1" },
     { name = "ruff", specifier = ">=0.12.1" },
 ]
+fp8-inference = [{ name = "deep-gemm", url = "https://github.com/hallerite/DeepGEMM/releases/download/v2.3.0/deep_gemm-2.3.0+35c4bc8-cp312-cp312-linux_x86_64.whl" }]

 [[package]]
 name = "prime-sandboxes"
PATCH

echo "Patch applied"
