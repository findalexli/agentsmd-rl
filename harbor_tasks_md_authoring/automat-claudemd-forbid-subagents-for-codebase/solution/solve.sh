#!/usr/bin/env bash
set -euo pipefail

cd /workspace/automat

# Idempotency guard
if grep -qF "- **Do not use sub-agents (Agent / Task / Explore) for codebase exploration.** R" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,3 +1,8 @@
+## Working in this codebase
+
+- **Do not use sub-agents (Agent / Task / Explore) for codebase exploration.** Read the actual source files yourself with Read/Grep/Glob. Sub-agent summaries are lossy and have introduced factual errors about this codebase (inventing globals, misreading init order, misattributing ownership). When in doubt, open the file.
+- The authoritative list of process-wide state lives in `src/automat.hh` and `src/root_widget.hh`. Init and teardown order is explicit in `automat::Main()` in `src/automat.cc`.
+
 ## Common Development Commands
 
 If along the way you execute some command, it doesn't work and then you figure out how to make it work, please record that in CLAUDE.md - this way you'll avoid making the same mistakes over and over.
PATCH

echo "Gold patch applied."
