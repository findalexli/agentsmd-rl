#!/usr/bin/env bash
set -euo pipefail

cd /workspace/orca

# Idempotency guard
if grep -qF "Keep comments short \u2014 one or two lines. Capture only the non-obvious reason (saf" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,8 +1,10 @@
 # AGENTS.md
 
-## Code Comments: Document the "Why"
+## Code Comments: Document the "Why", Briefly
 
-When writing or modifying code driven by a design doc or non-obvious constraint, you **must** add a comment explaining **why** the code behaves the way it does.
+When writing or modifying code driven by a design doc or non-obvious constraint, add a comment explaining **why** the code behaves the way it does.
+
+Keep comments short — one or two lines. Capture only the non-obvious reason (safety constraint, compatibility shim, design-doc rule). Don't restate what the code does, narrate the mechanism, cite design-doc sections verbatim, or explain adjacent API choices unless they're the point.
 
 ## File and Module Naming
 
@@ -22,4 +24,4 @@ Orca targets macOS, Linux, and Windows. Keep all platform-dependent behavior beh
 
 ## GitHub CLI Usage
 
-Be mindful of the user's `gh` CLI API rate limit — batch requests where possible and avoid unnecessary calls. All code, commands, and scripts must be compatible with macOS, Linux, and Windows.
+Be mindful of the user's `gh` CLI API rate limit — batch requests where possible and avoid unnecessary calls. All code, commands, and scripts must be compatible with macOS, Linux, and Windows.
\ No newline at end of file
PATCH

echo "Gold patch applied."
