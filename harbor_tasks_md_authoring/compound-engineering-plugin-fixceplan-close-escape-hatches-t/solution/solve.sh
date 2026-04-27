#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "description: \"Create structured plans for any multi-step task -- software featur" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -1,14 +1,16 @@
 ---
 name: ce:plan
-description: "Create structured plans for any multi-step task -- software features, research workflows, events, study plans, or any goal that benefits from structured breakdown. Also deepen existing plans with interactive review of sub-agent findings. Use for plan creation when the user says 'plan this', 'create a plan', 'write a tech plan', 'plan the implementation', 'how should we build', 'what's the approach for', 'break this down', 'plan a trip', 'create a study plan', or when a brainstorm/requirements document is ready for planning. Use for plan deepening when the user says 'deepen the plan', 'deepen my plan', 'deepening pass', or uses 'deepen' in reference to a plan. For exploratory or ambiguous requests where the user is unsure what to do, prefer ce:brainstorm first."
+description: "Create structured plans for any multi-step task -- software features, research workflows, events, study plans, or any goal that benefits from structured breakdown. Also deepen existing plans with interactive review of sub-agent findings. Use for plan creation when the user says 'plan this', 'create a plan', 'write a tech plan', 'plan the implementation', 'how should we build', 'what's the approach for', 'break this down', 'plan a trip', 'create a study plan', or when a brainstorm/requirements document is ready for planning. Use for plan deepening when the user says 'deepen the plan', 'deepen my plan', 'deepening pass', or uses 'deepen' in reference to a plan."
 argument-hint: "[optional: feature description, requirements doc path, plan path to deepen, or any task to plan]"
 ---
 
 # Create Technical Plan
 
 **Note: The current year is 2026.** Use this when dating plans and searching for recent documentation.
 
-`ce:brainstorm` defines **WHAT** to build. `ce:plan` defines **HOW** to build it. `ce:work` executes the plan.
+`ce:brainstorm` defines **WHAT** to build. `ce:plan` defines **HOW** to build it. `ce:work` executes the plan. A prior brainstorm is useful context but never required — `ce:plan` works from any input: a requirements doc, a bug report, a feature idea, or a rough description.
+
+**When directly invoked, always plan.** Never classify a direct invocation as "not a planning task" and abandon the workflow. If the input is unclear, ask clarifying questions or use the planning bootstrap (Phase 0.4) to establish enough context — but always stay in the planning workflow.
 
 This workflow produces a durable implementation plan. It does **not** implement code, run tests, or learn from execution-time results. If the answer depends on changing code and seeing what happens, that belongs in `ce:work`, not here.
 
@@ -22,9 +24,9 @@ Ask one question at a time. Prefer a concise single-select choice when natural o
 
 <feature_description> #$ARGUMENTS </feature_description>
 
-**If the feature description above is empty, ask the user:** "What would you like to plan? Describe the task, goal, or project you have in mind."
+**If the feature description above is empty, ask the user:** "What would you like to plan? Describe the task, goal, or project you have in mind." Then wait for their response before continuing.
 
-Do not proceed until you have a clear planning input.
+If the input is present but unclear or underspecified, do not abandon — ask one or two clarifying questions, or proceed to Phase 0.4's planning bootstrap to establish enough context. The goal is always to help the user plan, never to exit the workflow.
 
 **IMPORTANT: All file references in the plan document must use repo-relative paths (e.g., `src/models/user.rb`), never absolute paths (e.g., `/Users/name/Code/project/src/models/user.rb`). This applies everywhere — implementation unit file lists, pattern references, origin document links, and prose mentions. Absolute paths break portability across machines, worktrees, and teammates.**
 
@@ -83,7 +85,7 @@ If the task is about a non-software domain and describes a multi-step goal worth
 
 If genuinely ambiguous (e.g., "plan a migration" with no other context), ask the user before routing.
 
-For everything else (quick questions, error messages, factual lookups), respond directly without any planning workflow.
+For everything else (quick questions, error messages, factual lookups) **only when auto-selected**, respond directly without any planning workflow. When directly invoked by the user, treat the input as a planning request — ask clarifying questions if needed, but do not exit the workflow.
 
 #### 0.2 Find Upstream Requirements Document
 
@@ -114,12 +116,12 @@ If a relevant requirements document exists:
 
 If no relevant requirements document exists, planning may proceed from the user's request directly.
 
-#### 0.4 No-Requirements-Doc Fallback
+#### 0.4 Planning Bootstrap (No Requirements Doc or Unclear Input)
 
-If no relevant requirements document exists:
-- Assess whether the request is already clear enough for direct technical planning
-- If the ambiguity is mainly product framing, user behavior, or scope definition, recommend `ce:brainstorm` first
-- If the user wants to continue here anyway, run a short planning bootstrap instead of refusing
+If no relevant requirements document exists, or the input needs more structure:
+- Assess whether the request is already clear enough for direct technical planning — if so, continue to Phase 0.5
+- If the ambiguity is mainly product framing, user behavior, or scope definition, recommend `ce:brainstorm` as a suggestion — but always offer to continue planning here as well
+- If the user wants to continue here (or was already explicit about wanting a plan), run the planning bootstrap below
 
 The planning bootstrap should establish:
 - Problem frame
@@ -134,6 +136,11 @@ If the bootstrap uncovers major unresolved product questions:
 - Recommend `ce:brainstorm` again
 - If the user still wants to continue, require explicit assumptions before proceeding
 
+If the bootstrap reveals that a different workflow would serve the user better:
+
+- **Symptom without a root cause** (user describes broken behavior but hasn't identified why) — announce that investigation is needed before planning and load the `ce:debug` skill. A plan requires a known problem to solve; debugging identifies what that problem is. Announce the routing clearly: "This needs investigation before planning — switching to ce:debug to find the root cause."
+- **Clear task ready to execute** (known root cause, obvious fix, no architectural decisions) — suggest `ce:work` as a faster alternative alongside continuing with planning. The user decides.
+
 #### 0.5 Classify Outstanding Questions Before Planning
 
 If the origin document contains `Resolve Before Planning` or similar blocking questions:
PATCH

echo "Gold patch applied."
