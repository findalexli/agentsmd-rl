#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotency guard
if grep -qF "**IMPORTANT**: The product name \"goose\" should ALWAYS be written in lowercase \"g" "documentation/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/documentation/AGENTS.md b/documentation/AGENTS.md
@@ -0,0 +1,21 @@
+# Documentation Style Guide
+
+## Brand Guidelines
+
+**IMPORTANT**: The product name "goose" should ALWAYS be written in lowercase "g" in all documentation, blog posts, and any content within this documentation directory.
+
+- ✅ Correct: "goose", "using goose", "goose provides"
+- ❌ Incorrect: "Goose", "using Goose", "Goose provides"
+
+This is a brand guideline that must be strictly followed.
+
+## Context
+
+This rule applies to:
+- All markdown files in `/docs/`
+- All blog posts in `/blog/`
+- README files
+- Configuration files with user-facing text
+- Any other documentation content
+
+When editing or creating content in this documentation directory, always ensure "goose" uses a lowercase "g".
PATCH

echo "Gold patch applied."
