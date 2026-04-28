#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wp-calypso

# Idempotency guard
if grep -qF "- CRITICAL: Preserve existing curly quotes and apostrophes (\u201c\u201d \u2018\u2019) exactly as th" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1 +1,3 @@
 @AGENTS.md
+
+- CRITICAL: Preserve existing curly quotes and apostrophes (“” ‘’) exactly as they appear in the source. Do NOT replace them with unicode escape sequences (\u2019, etc.) or straight ASCII equivalents (', "). To do that, when editing strings that contain a mix of straight quote delimiters and curly quotes/apostrophes inside, avoid including the string delimiters in the old_string/new_string of the Edit tool. Instead, match on a unique inner substring that doesn't include the delimiters. This prevents the Edit tool from inadvertently converting straight quote delimiters to curly quotes or vice versa.
PATCH

echo "Gold patch applied."
