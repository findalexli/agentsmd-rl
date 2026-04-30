#!/usr/bin/env bash
set -euo pipefail

cd /workspace/etl

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "This file provides guidance to automation agents working with code in this repos" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,6 +1,6 @@
-# CLAUDE.md
+# Agent Guide
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance to automation agents working with code in this repository.
 
 # Individual Preferences
 - @~/.claude/instructions/etl.md
PATCH

echo "Gold patch applied."
