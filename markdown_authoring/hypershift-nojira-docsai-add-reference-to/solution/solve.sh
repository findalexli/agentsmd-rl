#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hypershift

# Idempotency guard
if grep -qF "The Effective Go skill is automatically enabled for all Go development. Just ask" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,8 @@
 # HyperShift Claude Code Configuration
 
-This repository includes Claude Code configuration for enhanced development assistance.
+This repository includes Claude Code specific configuration for enhanced development assistance.
+
+Please also refer to @AGENTS.md for guidance to all AI agents when working with code in this repository.
 
 ## Documentation
 
@@ -9,4 +11,4 @@ This repository includes Claude Code configuration for enhanced development assi
 
 ## Quick Start
 
-The Effective Go skill is automatically enabled for all Go development. Just ask Claude to write or review Go code, and best practices will be automatically applied.
\ No newline at end of file
+The Effective Go skill is automatically enabled for all Go development. Just ask Claude to write or review Go code, and best practices will be automatically applied.
PATCH

echo "Gold patch applied."
