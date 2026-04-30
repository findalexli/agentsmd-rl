#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "**If AUTOPILOT is active:** Present the plan briefly and proceed immediately. Do" "plan/SKILL.md" && grep -qF "**If AUTOPILOT is active:** Skip this question. Go directly to Next Step (compou" "ship/SKILL.md" && grep -qF "**If AUTOPILOT is active:** Do NOT ask clarifying questions. Work with the infor" "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -146,9 +146,11 @@ If the plan is a pure library with no user-facing output, skip this section.
 
 ### 7. Present and Confirm
 
-Present the plan to the user. Wait for explicit approval before executing. If the user modifies the plan, update it before proceeding.
+**If AUTOPILOT is active:** Present the plan briefly and proceed immediately. Do not wait for approval. The user chose autopilot because they trust the process.
 
-After the user approves, do these two steps in order:
+**Otherwise:** Present the plan to the user. Wait for explicit approval before executing. If the user modifies the plan, update it before proceeding.
+
+After the plan is approved (or auto-approved in autopilot), do these two steps in order:
 
 **Step 1: Save the artifact.** Run this command now — do not skip it:
 
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -196,9 +196,11 @@ Or pass full JSON for richer detail:
 ~/.claude/skills/nanostack/bin/sprint-journal.sh
 ```
 
-**Step 2: Ask how the user wants to see the result.**
+**Step 2: How to see the result.**
 
-Ask:
+**If AUTOPILOT is active:** Skip this question. Go directly to Next Step (compound + sprint summary). The user will decide how to run it after the sprint closes.
+
+**Otherwise**, ask:
 > How do you want to see it?
 > 1. Local — I'll start the server and show you how to open it
 > 2. Production — I'll guide you through deploying to the internet
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -67,6 +67,8 @@ Understand the landscape, then determine the mode.
 
 **If the user didn't provide an idea or problem** (e.g. they just said `/think` or `/think --autopilot` with no context), simply ask in your response: "What do you want to build?" Do NOT use `AskUserQuestion` for this. Just ask in plain text and wait for their reply.
 
+**If AUTOPILOT is active:** Do NOT ask clarifying questions. Work with the information provided. Default to Builder mode. If the description is clear enough to plan, skip the diagnostic questions and go straight to Phase 5 (scope recommendation) with a brief that covers value prop, scope, wedge and risk. The user chose autopilot because they want speed, not a conversation.
+
 Determine the mode from the user's description:
 
 - **Founder mode**: Experienced entrepreneur stress-testing an idea. Wants to be challenged hard. Applies full YC diagnostic with maximum pushback. Use when the user explicitly asks for a tough review or says something like "tear this apart."
PATCH

echo "Gold patch applied."
