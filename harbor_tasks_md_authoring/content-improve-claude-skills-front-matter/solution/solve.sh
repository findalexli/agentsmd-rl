#!/usr/bin/env bash
set -euo pipefail

cd /workspace/content

# Idempotency guard
if grep -qF "description: Search for existing rules that match a given requirement text. Iden" ".claude/skills/find-rule/SKILL.md" && grep -qF "description: Create or update a versioned profile pair (versioned + unversioned " ".claude/skills/manage-profile/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/find-rule/SKILL.md b/.claude/skills/find-rule/SKILL.md
@@ -1,5 +1,6 @@
 ---
-disable-model-invocation: true
+name: find-rule
+description: Search for existing rules that match a given requirement text. Identify rules that implement a specific control.
 ---
 
 Search for existing rules that match the following requirement:
diff --git a/.claude/skills/manage-profile/SKILL.md b/.claude/skills/manage-profile/SKILL.md
@@ -1,4 +1,6 @@
 ---
+name: manage-profile
+description: Create or update a versioned profile pair (versioned + unversioned extends pattern).
 disable-model-invocation: true
 ---
 
PATCH

echo "Gold patch applied."
