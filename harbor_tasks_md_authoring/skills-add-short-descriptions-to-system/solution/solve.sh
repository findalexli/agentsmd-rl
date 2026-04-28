#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "short-description: Generate a plan for a complex task" "skills/.system/plan/SKILL.md" && grep -qF "The skill should only contain the information needed for an AI agent to do the j" "skills/.system/skill-creator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/.system/plan/SKILL.md b/skills/.system/plan/SKILL.md
@@ -1,6 +1,8 @@
 ---
 name: plan
 description: Generate a plan for how an agent should accomplish a complex coding task. Use when a user asks for a plan, and optionally when they want to save, find, read, update, or delete plan files in $CODEX_HOME/plans (default ~/.codex/plans).
+metadata:
+  short-description: Generate a plan for a complex task
 ---
 
 # Plan
diff --git a/skills/.system/skill-creator/SKILL.md b/skills/.system/skill-creator/SKILL.md
@@ -1,6 +1,8 @@
 ---
 name: skill-creator
 description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations.
+metadata:
+  short-description: Create or update a skill
 ---
 
 # Skill Creator
@@ -108,7 +110,7 @@ A skill should only contain essential files that directly support its functional
 - CHANGELOG.md
 - etc.
 
-The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.
+The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.
 
 ### Progressive Disclosure Design Principle
 
PATCH

echo "Gold patch applied."
