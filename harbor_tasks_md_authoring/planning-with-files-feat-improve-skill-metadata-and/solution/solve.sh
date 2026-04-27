#!/usr/bin/env bash
set -euo pipefail

cd /workspace/planning-with-files

# Idempotency guard
if grep -qF "description: Implements Manus-style file-based planning to organize and track pr" "skills/planning-with-files/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/planning-with-files/SKILL.md b/skills/planning-with-files/SKILL.md
@@ -1,17 +1,8 @@
 ---
 name: planning-with-files
-version: "2.10.0"
-description: Implements Manus-style file-based planning for complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when starting complex multi-step tasks, research projects, or any task requiring >5 tool calls. Now with automatic session recovery after /clear.
+description: Implements Manus-style file-based planning to organize and track progress on complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when asked to plan out, break down, or organize a multi-step project, research task, or any work requiring >5 tool calls. Supports automatic session recovery after /clear.
 user-invocable: true
-allowed-tools:
-  - Read
-  - Write
-  - Edit
-  - Bash
-  - Glob
-  - Grep
-  - WebFetch
-  - WebSearch
+allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch"
 hooks:
   PreToolUse:
     - matcher: "Write|Edit|Bash|Read|Glob|Grep"
@@ -51,6 +42,8 @@ hooks:
             else
               sh "$SCRIPT_DIR/check-complete.sh"
             fi
+metadata:
+  version: "2.10.0"
 ---
 
 # Planning with Files
PATCH

echo "Gold patch applied."
