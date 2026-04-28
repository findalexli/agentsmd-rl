#!/usr/bin/env bash
set -euo pipefail

cd /workspace/eris

# Idempotency guard
if grep -qF "When performing a code review, make sure all properties/methods in classes and o" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,3 @@
+When performing a code review, make sure all properties/methods in classes and objects, where applicable, and including documentation, is listed in alphabetical order. The only exceptions to this are `update()` method in classes, which should appear first, and `toString()`/`toJSON()` should appear last.
+
+When performing a code review, make sure class getters are positioned before class methods.
\ No newline at end of file
PATCH

echo "Gold patch applied."
