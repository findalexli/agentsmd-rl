#!/usr/bin/env bash
set -euo pipefail

cd /workspace/codex

# Idempotency guard
if grep -qF "short-description: Generate a plan for a complex task" "codex-rs/core/src/skills/assets/samples/plan/SKILL.md" && grep -qF "short-description: Create or update a skill" "codex-rs/core/src/skills/assets/samples/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/codex-rs/core/src/skills/assets/samples/plan/SKILL.md b/codex-rs/core/src/skills/assets/samples/plan/SKILL.md
@@ -2,7 +2,7 @@
 name: plan
 description: Generate a plan for how an agent should accomplish a complex coding task. Use when a user asks for a plan, and optionally when they want to save, find, read, update, or delete plan files in $CODEX_HOME/plans (default ~/.codex/plans).
 metadata:
-  short-description: Create and manage plan markdown files under $CODEX_HOME/plans.
+  short-description: Generate a plan for a complex task
 ---
 
 # Plan
diff --git a/codex-rs/core/src/skills/assets/samples/skill-creator/SKILL.md b/codex-rs/core/src/skills/assets/samples/skill-creator/SKILL.md
@@ -1,6 +1,8 @@
 ---
 name: skill-creator
 description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations.
+metadata:
+  short-description: Create or update a skill
 ---
 
 # Skill Creator
PATCH

echo "Gold patch applied."
