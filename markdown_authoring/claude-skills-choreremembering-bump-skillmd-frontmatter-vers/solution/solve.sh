#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "version: 5.7.1" "remembering/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/remembering/SKILL.md b/remembering/SKILL.md
@@ -2,7 +2,7 @@
 name: remembering
 description: Advanced memory operations reference. Basic patterns (profile loading, simple recall/remember) are in project instructions. Consult this skill for background writes, memory versioning, complex queries, edge cases, session scoping, retention management, type-safe results, proactive memory hints, GitHub access detection, autonomous curation, episodic scoring, and decision traces.
 metadata:
-  version: 5.4.0
+  version: 5.7.1
 ---
 
 # Remembering - Advanced Operations
PATCH

echo "Gold patch applied."
