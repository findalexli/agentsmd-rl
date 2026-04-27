#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Check the skill arguments for `mode:headless`. Arguments may contain a document " "plugins/compound-engineering/skills/document-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/document-review/SKILL.md b/plugins/compound-engineering/skills/document-review/SKILL.md
@@ -1,17 +1,40 @@
 ---
 name: document-review
 description: Review requirements or plan documents using parallel persona agents that surface role-specific issues. Use when a requirements document or plan document exists and the user wants to improve it.
+argument-hint: "[path/to/document.md]"
 ---
 
 # Document Review
 
 Review requirements or plan documents through multi-persona analysis. Dispatches specialized reviewer agents in parallel, auto-fixes quality issues, and presents strategic questions for user decision.
 
+## Phase 0: Detect Mode
+
+Check the skill arguments for `mode:headless`. Arguments may contain a document path, `mode:headless`, or both. Tokens starting with `mode:` are flags, not file paths -- strip them from the arguments and use the remaining token (if any) as the document path for Phase 1.
+
+If `mode:headless` is present, set **headless mode** for the rest of the workflow.
+
+**Headless mode** changes the interaction model, not the classification boundaries. Document-review still applies the same judgment about what is deterministic vs. what needs verification. The only difference is how non-auto findings are delivered:
+- `auto` fixes are applied silently (same as interactive)
+- `batch_confirm` and `present` findings are returned as structured text for the caller to handle -- no AskUserQuestion prompts, no interactive approval
+- Phase 5 returns immediately with "Review complete" (no refine/complete question)
+
+The caller receives findings with their original classifications intact and decides what to do with each tier.
+
+Callers invoke headless mode by including `mode:headless` in the skill arguments, e.g.:
+```
+Skill("compound-engineering:document-review", "docs/plans/my-plan.md mode:headless")
+```
+
+If `mode:headless` is not present, the skill runs in its default interactive mode with no behavior change.
+
 ## Phase 1: Get and Analyze Document
 
 **If a document path is provided:** Read it, then proceed.
 
-**If no document is specified:** Ask which document to review, or find the most recent in `docs/brainstorms/` or `docs/plans/` using a file-search/glob tool (e.g., Glob in Claude Code).
+**If no document is specified (interactive mode):** Ask which document to review, or find the most recent in `docs/brainstorms/` or `docs/plans/` using a file-search/glob tool (e.g., Glob in Claude Code).
+
+**If no document is specified (headless mode):** Output "Review failed: headless mode requires a document path. Re-invoke with: Skill(\"compound-engineering:document-review\", \"<path> mode:headless\")" without dispatching agents.
 
 ### Classify Document Type
 
@@ -173,6 +196,10 @@ Apply all `auto` findings to the document in a **single pass**:
 
 If any `batch_confirm` findings exist:
 
+**Headless mode:** Do not prompt. Include `batch_confirm` findings in the structured text output alongside `present` findings, clearly marked with their classification so the caller can distinguish them. The caller decides whether to apply them.
+
+**Interactive mode:**
+
 1. Present the proposed fixes in a numbered table (see template)
 2. **Ask for approval using the platform's interactive question tool** -- do not print the question as plain text output:
    - Claude Code: `AskUserQuestion`
@@ -189,6 +216,40 @@ This turns N obvious-but-meaning-touching fixes into 1 interaction instead of N.
 
 ### Present Remaining Findings
 
+**Headless mode:** Do not use interactive question tools. Output all non-auto findings as a structured text summary the caller can parse and act on:
+
+```
+Document review complete (headless mode).
+
+Applied N auto-fixes.
+
+Batch-confirm findings (clear fix, wording needs verification):
+
+[P1][batch_confirm] Section: <section> — <title> (<reviewer>, confidence <N>)
+  Why: <why_it_matters>
+  Suggested fix: <suggested_fix>
+
+Present findings (requires judgment):
+
+[P0][present] Section: <section> — <title> (<reviewer>, confidence <N>)
+  Why: <why_it_matters>
+  Suggested fix: <suggested_fix or "none">
+
+[P1][present] Section: <section> — <title> (<reviewer>, confidence <N>)
+  Why: <why_it_matters>
+  Suggested fix: <suggested_fix or "none">
+
+Residual concerns:
+- <concern> (<source>)
+
+Deferred questions:
+- <question> (<source>)
+```
+
+Omit any section with zero items. Then proceed directly to Phase 5 (which returns immediately in headless mode).
+
+**Interactive mode:**
+
 Present `present` findings using the review output template included below. Within each severity level, separate findings by type:
 - **Errors** (design tensions, contradictions, incorrect statements) first -- these need resolution
 - **Omissions** (missing steps, absent details, forgotten entries) second -- these need additions
@@ -208,6 +269,10 @@ These are pipeline artifacts and must not be flagged for removal.
 
 ## Phase 5: Next Action
 
+**Headless mode:** Return "Review complete" immediately. Do not ask questions. The caller receives the text summary from Phase 4 and handles any remaining findings.
+
+**Interactive mode:**
+
 **Ask using the platform's interactive question tool** -- do not print the question as plain text output:
 - Claude Code: `AskUserQuestion`
 - Codex: `request_user_input`
@@ -229,7 +294,7 @@ Return "Review complete" as the terminal signal for callers.
 - Do not add new sections or requirements the user didn't discuss
 - Do not over-engineer or add complexity
 - Do not create separate review files or add metadata sections
-- Do not modify any of the 2 caller skills (ce-brainstorm, ce-plan)
+- Do not modify caller skills (ce-brainstorm, ce-plan, or external plugin skills that invoke document-review)
 
 ## Iteration Guidance
 
PATCH

echo "Gold patch applied."
