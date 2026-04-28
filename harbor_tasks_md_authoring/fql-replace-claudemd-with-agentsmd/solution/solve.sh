#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fql

# Idempotency guard
if grep -qF "This file provides guidance for AI coding agents working with code in this repos" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,6 @@
-# CLAUDE.md
+# AGENTS.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance for AI coding agents working with code in this repository.
 
 ## Project Overview
 
@@ -83,4 +83,4 @@ The build system uses Docker Compose for consistent builds:
 - `bake.hcl` defines Docker build configuration
 - `compose.yaml` defines runtime services (build, fql, fdb containers)
 - Use `--latest` flag for offline development
-- FDB container automatically managed for tests
\ No newline at end of file
+- FDB container automatically managed for tests
PATCH

echo "Gold patch applied."
