#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skill-temporal-developer

# Idempotency guard
if grep -qF "version: 0.3.1" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: temporal-developer
 description: Develop, debug, and manage Temporal applications across Python, TypeScript, Go, Java and .NET. Use when the user is building workflows, activities, or workers with a Temporal SDK, debugging issues like non-determinism errors, stuck workflows, or activity retries, using Temporal CLI, Temporal Server, or Temporal Cloud, or working with durable execution concepts like signals, queries, heartbeats, versioning, continue-as-new, child workflows, or saga patterns.
-version: 0.3.0
+version: 0.3.1
 ---
 
 # Skill: temporal-developer
PATCH

echo "Gold patch applied."
