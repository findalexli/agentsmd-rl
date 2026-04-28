#!/usr/bin/env bash
set -euo pipefail

cd /workspace/youtrackdb

# Idempotency guard
if grep -qF "All agent instructions are in [`CLAUDE.md`](CLAUDE.md). Read that file first." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,3 @@
+# AGENTS.md
+
+All agent instructions are in [`CLAUDE.md`](CLAUDE.md). Read that file first.
PATCH

echo "Gold patch applied."
