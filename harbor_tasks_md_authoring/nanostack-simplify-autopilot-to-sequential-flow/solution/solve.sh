#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "Proceed directly to `/review`. After review completes, run `/security`. After se" "plan/SKILL.md" && grep -qF "**If AUTOPILOT is active and tests pass:** Proceed to `/ship`. Show: `Autopilot:" "qa/SKILL.md" && grep -qF "**If AUTOPILOT is active and no blocking issues found:** Proceed directly to the" "review/SKILL.md" && grep -qF "**If AUTOPILOT is active and no critical/high findings:** Proceed to next pendin" "security/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -146,27 +146,18 @@ After the user approves the plan and you finish building:
 
 **If AUTOPILOT is active:**
 
-After build completes, run `/review`, `/security` and `/qa` **in parallel** using three Agent tool calls in a single message. These three phases are all read-only (they analyze code but don't modify it) and have no dependencies on each other.
-
-```
-Launch 3 agents in parallel (single message, 3 Agent tool calls):
-
-Agent 1: "Run /review on this project. Save the artifact when done. Return the summary."
-Agent 2: "Run /security on this project. Save the artifact when done. Return the summary."
-Agent 3: "Run /qa on this project. Save the artifact when done. Return the summary."
-```
-
-Show status as results come back:
-> Autopilot: running /review, /security and /qa in parallel...
-> Autopilot: review complete (X findings, 0 blocking).
-> Autopilot: security grade A (0 critical, 0 high).
-> Autopilot: qa passed (X tests, 0 failed).
-
-After all three complete, check results:
-- If any has **blocking issues**, **critical vulnerabilities**, or **test failures**: stop and ask the user
-- If all three pass: proceed to `/ship`
-
-If parallel execution is not available (single-threaded agent, no Agent tool), fall back to running them sequentially: `/review` → `/security` → `/qa`.
+Proceed directly to `/review`. After review completes, run `/security`. After security, run `/qa`. After all three pass, run `/ship`. Only stop if:
+- `/review` finds **blocking** issues that need user decision
+- `/security` finds **critical** vulnerabilities
+- A product question comes up that you can't answer from context
+
+Between each step, show a brief status:
+> Autopilot: build complete. Running /review...
+> Autopilot: review clean. Running /security...
+> Autopilot: security grade A. Running /qa...
+> Autopilot: qa passed. Running /ship...
+
+For parallel execution across multiple terminals, use `/conductor` instead of autopilot.
 
 **Otherwise (default):**
 
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -218,11 +218,9 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After QA is complete and the artifact is saved:
 
-**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+**If AUTOPILOT is active and tests pass:** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`
 
-**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`
-
-**If AUTOPILOT is active but tests fail:** Return the failures. The parent agent (or sequential flow) will stop and ask the user.
+**If AUTOPILOT is active but tests fail:** Stop and ask the user. Show failures and wait.
 
 **Otherwise:** Tell the user:
 > QA complete. Remaining steps:
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -154,11 +154,9 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After the review is complete and the artifact is saved:
 
-**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+**If AUTOPILOT is active and no blocking issues found:** Proceed directly to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /security...`
 
-**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /security...`
-
-**If AUTOPILOT is active but blocking issues found:** Return the blocking issues. The parent agent (or sequential flow) will stop and ask the user.
+**If AUTOPILOT is active but blocking issues found:** Stop and ask the user to resolve. Show the blocking issues and wait. After resolution, continue autopilot.
 
 **Otherwise:** Tell the user:
 > Review complete. Remaining steps:
diff --git a/security/SKILL.md b/security/SKILL.md
@@ -246,11 +246,9 @@ See `reference/artifact-schema.md` for the full schema. The user can disable aut
 
 After the security audit is complete and the artifact is saved:
 
-**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.
+**If AUTOPILOT is active and no critical/high findings:** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`
 
-**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`
-
-**If AUTOPILOT is active but critical or high findings found:** Return the findings. The parent agent (or sequential flow) will stop and ask the user.
+**If AUTOPILOT is active but critical or high findings found:** Stop and ask the user to review. Show the findings and wait. After resolution, continue autopilot.
 
 **Otherwise:** Tell the user:
 > Security audit complete. Remaining steps:
PATCH

echo "Gold patch applied."
