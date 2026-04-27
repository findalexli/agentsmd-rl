#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mc-agent-toolkit

# Idempotency guard
if grep -qF "**Action guard \u2014 workflow mode:** Never call write tools (`update_alert`, `set_a" "skills/automated-triage/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/automated-triage/SKILL.md b/skills/automated-triage/SKILL.md
@@ -1,12 +1,7 @@
 ---
 name: monte-carlo-automated-triage
-description: |
-  Guides users through setting up and running automated alert triage for
-  their Monte Carlo environment. Activates when a user asks to triage alerts,
-  set up automated triage, run agentic triage, or investigate recent alert
-  activity. Covers MCP setup, the stages of a triage workflow, and how to
-  customise each stage to match how their team responds to alerts manually.
-version: 1.0.0
+description: Triage Monte Carlo alerts interactively or build an automated workflow. Fetch, score, and troubleshoot alerts using MCP tools now, or design a reusable workflow that runs on a schedule.
+version: 1.1.0
 ---
 
 # Monte Carlo Automated Triage
@@ -24,6 +19,7 @@ Read the reference files before proceeding:
 
 Activate when the user:
 
+- Wants to triage or investigate recent Monte Carlo alerts (interactively or automated)
 - Wants to set up automated triage for Monte Carlo alerts
 - Asks to run agentic triage or investigate recent alert activity
 - Wants to understand what triage tools are available and how to use them
@@ -88,7 +84,32 @@ When this skill is activated, follow this sequence in order.
 
 Verify that `get_alerts`, `alert_assessment`, and `run_troubleshooting_agent` are accessible. If any are missing, check that the Monte Carlo MCP server is configured and authenticated, then stop.
 
-### Step 2: Orient the user to their workflow
+### Step 2: Determine intent
+
+Ask:
+
+> "Are you looking to **triage some alerts right now** (I'll investigate them with you using the triage tools), or **set up / refine an automated triage workflow** (I'll help you design a process that can run on a schedule)?"
+
+If the user's request already makes the intent clear — e.g. "triage my freshness alerts from today" vs. "help me build a triage workflow" — skip the question and proceed directly.
+
+---
+
+#### Branch A: Interactive triage
+
+The user wants to look at specific alerts now. Use the triage tools directly to investigate and report findings. Do not frame this as workflow-building.
+
+1. Clarify scope if needed — which alert types, time window, or specific tables? If the user already specified (e.g. "recent freshness alerts"), proceed without asking.
+2. Fetch alerts with `get_alerts`, run `alert_assessment` in parallel on all of them, and report the results clearly.
+3. For any alert where both confidence and impact are MEDIUM or higher, offer to run `run_troubleshooting_agent` for a deeper root cause analysis. Wait for confirmation before running it.
+4. Summarise findings. Do not prompt to save a workflow file or set up automation unless the user brings it up.
+
+**Write tools in interactive triage:** After findings are clear, proactively offer relevant actions — updating status, declaring a severity, assigning an owner, or posting a comment. Ask before executing.
+
+---
+
+#### Branch B: Automated workflow
+
+The user wants to build, test, or refine a triage workflow that can run on a schedule.
 
 Ask how they'd like to get started:
 
@@ -113,10 +134,12 @@ Ask how they'd like to get started:
 2. Draw on `references/triage-stages.md` to propose a workflow structure that fits their goals. Present it for review — not as a finished document, but as a proposed approach — and iterate until they're happy.
 3. Run it step by step in recommendation mode (see Step 3) so they can validate each stage before committing to the design. Expect to refine as you go.
 
-### Step 3: Run the workflow
+### Step 3: Run the workflow (Branch B only)
 
 Execute the workflow from the file, following its instructions exactly. Do not improvise steps or add actions not described in the file.
 
+**Action guard — workflow mode:** Never call write tools (`update_alert`, `set_alert_owner`, `create_or_update_alert_comment`) while building or testing a workflow, regardless of what the workflow document says. Only describe what would be done. This guard exists to prevent accidental writes on real alerts during development; lift it only when the user explicitly switches to action mode for a production run.
+
 **For first runs (starting fresh):** always run step by step — after each stage completes, summarise what it produced, proactively suggest alternatives or adjustments based on what you observed, and wait for confirmation before continuing.
 
 At each stage, draw on the options in `references/triage-stages.md` to make concrete suggestions:
PATCH

echo "Gold patch applied."
