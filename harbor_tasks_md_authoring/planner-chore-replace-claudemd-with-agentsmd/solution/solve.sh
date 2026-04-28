#!/usr/bin/env bash
set -euo pipefail

cd /workspace/planner

# Idempotency guard
if grep -qF "Docker setup exists in this repository (`bin/d*` commands) but is **not used** f" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,6 @@
-# CLAUDE.md
+# AGENTS.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance to AI agents when working with code in this repository.
 
 ## Project Overview
 
@@ -38,7 +38,7 @@ codebar planner is a Rails 8.1 application for managing [codebar.io](https://cod
 
 ### Docker Setup (Not Used)
 
-Docker setup exists in this repository (`bin/d*` commands) but is **not used** for development work with Claude Code.
+Docker setup exists in this repository (`bin/d*` commands) but is **not used** for development work with Claude Code, OpenCode, etc.
 
 ### Environment Variables
 
PATCH

echo "Gold patch applied."
