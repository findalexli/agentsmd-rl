#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry-cli

# Idempotency guard
if grep -qF "**ALWAYS** run `cargo fmt` before committing any Rust code changes to ensure con" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -76,3 +76,7 @@ Access the `.cursor/rules/` directory and read rule file contents. Parse the fro
 - **Parse frontmatter carefully** - use the metadata to determine rule applicability
 
 Treat these rules as **mandatory guidance** that you must follow for all code changes and development activities within this project.
+
+# Code Formatting
+
+**ALWAYS** run `cargo fmt` before committing any Rust code changes to ensure consistent formatting across the codebase.
PATCH

echo "Gold patch applied."
