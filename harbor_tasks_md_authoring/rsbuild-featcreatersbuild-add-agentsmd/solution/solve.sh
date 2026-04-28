#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rsbuild

# Idempotency guard
if grep -qF "You are an expert in JavaScript, Rsbuild, and web application development. You w" "packages/create-rsbuild/template-common/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/create-rsbuild/template-common/AGENTS.md b/packages/create-rsbuild/template-common/AGENTS.md
@@ -0,0 +1,14 @@
+# AGENTS.md
+
+You are an expert in JavaScript, Rsbuild, and web application development. You write maintainable, performant, and accessible code.
+
+## Commands
+
+- `npm run dev` - Start the dev server
+- `npm run build` - Build the app for production
+- `npm run preview` - Preview the production build locally
+
+## Docs
+
+- Rsbuild: <https://rsbuild.rs/llms.txt>
+- Rspack: <https://rspack.rs/llms.txt>
PATCH

echo "Gold patch applied."
