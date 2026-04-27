#!/usr/bin/env bash
set -euo pipefail

cd /workspace/plannotator

# Idempotency guard
if grep -qF "a polished HTML dashboard report." "apps/skills/plannotator-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/skills/plannotator-compound/SKILL.md b/apps/skills/plannotator-compound/SKILL.md
@@ -1,13 +1,10 @@
 ---
 name: plannotator-compound
+disable-model-invocation: true
 description: >
   Analyze a user's Plannotator plan archive to extract denial patterns, feedback
   taxonomy, evolution over time, and actionable prompt improvements — then produce
-  a polished HTML dashboard report. Use this skill when the user says things like
-  "/compound-planning", "analyze my plans", "plan analysis", "what are my denial
-  patterns", "why do my plans get denied", "compound planning report", "plan
-  insights", or "analyze my planning data". This is a user-invoked skill only —
-  do not trigger automatically. The user must explicitly request it.
+  a polished HTML dashboard report.
 ---
 
 # Compound Planning Analysis
PATCH

echo "Gold patch applied."
