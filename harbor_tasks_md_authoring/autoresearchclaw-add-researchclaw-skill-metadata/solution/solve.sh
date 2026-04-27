#!/usr/bin/env bash
set -euo pipefail

cd /workspace/autoresearchclaw

# Idempotency guard
if grep -qF "description: Run the ResearchClaw autonomous research pipeline from a topic, con" ".claude/skills/researchclaw/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/researchclaw/SKILL.md b/.claude/skills/researchclaw/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: researchclaw
+description: Run the ResearchClaw autonomous research pipeline from a topic, config, and output directory.
+---
+
 # ResearchClaw — Autonomous Research Pipeline Skill
 
 ## Description
PATCH

echo "Gold patch applied."
