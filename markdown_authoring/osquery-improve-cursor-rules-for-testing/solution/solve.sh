#!/usr/bin/env bash
set -euo pipefail

cd /workspace/osquery

# Idempotency guard
if grep -qF "- When running tests, always use -DOSQUERY_BUILD_TESTS=ON to enable building tes" ".cursor/rules/build-format.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/build-format.mdc b/.cursor/rules/build-format.mdc
@@ -1,5 +1,5 @@
 ---
-description: Build and format configurations
+description: Build, test, and format
 alwaysApply: true
 
 - This project uses CMake.
@@ -8,6 +8,8 @@ alwaysApply: true
 - Always run make commands in the build/ subdirectory in the root of the repository.
 - When adding new files, edit the appropriate CMakeLists.txt.
 - Look for osqueryi and osqueryd binaries in the build/osquery directory.
-- Use -DOSQUERY_BUILD_TESTS=ON to enable building tests. This makes builds take longer, so only do it when tests are needed.
+- When manually testing, use ./osquery/osqueryi unless it is necessary to run in daemon mode.
+- Always rebuild before testing.
+- When running tests, always use -DOSQUERY_BUILD_TESTS=ON to enable building tests. This makes builds take longer, so only do it when tests are needed.
 - Format the code as specified in .clang-format. Check formatting is correct with `cmake --build . --target format_check`.
 ---
PATCH

echo "Gold patch applied."
