#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-" "plugins/compound-engineering/skills/lfg/SKILL.md" && grep -qF "1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-" "plugins/compound-engineering/skills/slfg/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/lfg/SKILL.md b/plugins/compound-engineering/skills/lfg/SKILL.md
@@ -7,7 +7,7 @@ disable-model-invocation: true
 
 CRITICAL: You MUST execute every step below IN ORDER. Do NOT skip any required step. Do NOT jump ahead to coding or implementation. The plan phase (step 2, and step 3 when warranted) MUST be completed and verified BEFORE any work begins. Violating this order produces bad output.
 
-1. **Optional:** If the `ralph-wiggum` skill is available, run `/ralph-wiggum:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2 immediately.
+1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2 immediately.
 
 2. `/ce:plan $ARGUMENTS`
 
@@ -33,4 +33,4 @@ CRITICAL: You MUST execute every step below IN ORDER. Do NOT skip any required s
 
 9. Output `<promise>DONE</promise>` when video is in PR
 
-Start with step 2 now (or step 1 if ralph-wiggum is available). Remember: plan FIRST, then work. Never skip the plan.
+Start with step 2 now (or step 1 if ralph-loop is available). Remember: plan FIRST, then work. Never skip the plan.
diff --git a/plugins/compound-engineering/skills/slfg/SKILL.md b/plugins/compound-engineering/skills/slfg/SKILL.md
@@ -9,7 +9,7 @@ Swarm-enabled LFG. Run these steps in order, parallelizing where indicated. Do n
 
 ## Sequential Phase
 
-1. **Optional:** If the `ralph-wiggum` skill is available, run `/ralph-wiggum:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2 immediately.
+1. **Optional:** If the `ralph-loop` skill is available, run `/ralph-loop:ralph-loop "finish all slash commands" --completion-promise "DONE"`. If not available or it fails, skip and continue to step 2 immediately.
 2. `/ce:plan $ARGUMENTS`
 3. **Conditionally** run `/compound-engineering:deepen-plan`
    - Run the `deepen-plan` workflow only if the plan is `Standard` or `Deep`, touches a high-risk area (auth, security, payments, migrations, external APIs, significant rollout concerns), or still has obvious confidence gaps in decisions, sequencing, system-wide impact, risks, or verification
PATCH

echo "Gold patch applied."
