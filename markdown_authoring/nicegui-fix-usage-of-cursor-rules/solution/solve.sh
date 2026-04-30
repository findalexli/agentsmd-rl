#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nicegui

# Idempotency guard
if grep -qF "2. [AGENTS.md](../../AGENTS.md) - AI agent guidelines and code review instructio" ".cursor/rules/general.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/general.mdc b/.cursor/rules/general.mdc
@@ -1,10 +1,14 @@
+---
+alwaysApply: true
+---
+
 # Cursor AI Quick Reference
 
 **Read these files before working:**
 
-1. [README.md](../README.md) - Project overview and setup
-2. [AGENTS.md](../AGENTS.md) - AI agent guidelines and code review instructions
-3. [CONTRIBUTING.md](../CONTRIBUTING.md) - Coding standards and workflow
+1. [README.md](../../README.md) - Project overview and setup
+2. [AGENTS.md](../../AGENTS.md) - AI agent guidelines and code review instructions
+3. [CONTRIBUTING.md](../../CONTRIBUTING.md) - Coding standards and workflow
 
 ## Quick Reference
 
PATCH

echo "Gold patch applied."
