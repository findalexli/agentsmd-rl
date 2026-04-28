#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fcitx5-mcbopomofo

# Idempotency guard
if grep -qF "- Do point out spelling errors in symbol names such as those of variables, class" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,12 @@
+When reviewing code:
+
+- Do NOT generate pull request overviews.
+- Do NOT generate explainers.
+- Do NOT summarize what a diff chunk does.
+- Only point out issues that are of medium severity or higher.
+- Do point out spelling errors in symbol names such as those of variables, classes, methods, and functions.
+- Do point out spelling or grammar errors in comments.
+- Do point out style issues such as extraneous spaces (for example `a  = b;`).
+- Do point out spelling errors in commit messages.
+- Do point out issues surrounding C++ `auto` uses. Suggest when `const auto&` can be used, for example.
+
PATCH

echo "Gold patch applied."
