#!/usr/bin/env bash
set -euo pipefail

cd /workspace/revm

# Idempotency guard
if grep -qF "- Update relevant examples if needed" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -19,7 +19,7 @@ cargo build
 cargo build --release
 
 # Run all tests
-cargo nexttest run --workspace
+cargo nextest run --workspace
 
 # Lint and format
 cargo clippy --workspace --all-targets --all-features
@@ -91,4 +91,4 @@ When adding new features:
 - Ensure no_std compatibility
 - Add appropriate feature flags
 - Include tests for new functionality
-- Update relevant examples if needed
\ No newline at end of file
+- Update relevant examples if needed
PATCH

echo "Gold patch applied."
