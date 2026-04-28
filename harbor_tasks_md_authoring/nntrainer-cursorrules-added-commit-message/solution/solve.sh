#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nntrainer

# Idempotency guard
if grep -qF "- If the commit is a bugfix; it should describe the bug and how it is resolved." ".cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -6,6 +6,12 @@
 
 You are reviewing and editing code in the nntrainer repository.
 
+=== How to write commit messages ===
+- The commit message should summarize the commit itself.
+- If the commit is a bugfix; it should describe the bug and how it is resolved.
+- If the commit is a new feature; it should describe the feature itself.
+- A commit should include a sign-off message.
+
 === Project context / build system ===
 - Primary language: C++ (C++17 is used).
 - Build system: Meson + Ninja.
PATCH

echo "Gold patch applied."
