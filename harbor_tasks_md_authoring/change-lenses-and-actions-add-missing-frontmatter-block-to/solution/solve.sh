#!/usr/bin/env bash
set -euo pipefail

cd /workspace/change-lenses-and-actions

# Idempotency guard
if grep -qF "description: Run a structured behavioral diagnosis using COM-B, the Behavior Cha" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: com-b-diagnostic
+description: Run a structured behavioral diagnosis using COM-B, the Behavior Change Wheel, and BCT Taxonomy v1. Activate when the user describes a stuck or problematic behavior, or uses phrases like "Why aren't people doing X?", "Run a COM-B analysis", "Diagnose this behavior", or "What's blocking adoption of X?"
+---
+
 # COM-B Diagnostic Skill
 
 ## Purpose
PATCH

echo "Gold patch applied."
