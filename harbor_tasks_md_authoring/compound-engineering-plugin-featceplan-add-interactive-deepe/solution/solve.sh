#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "description: \"Transform feature descriptions or requirements into structured imp" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:plan
-description: "Transform feature descriptions or requirements into structured implementation plans grounded in repo patterns and research. Use when the user says 'plan this', 'create a plan', 'write a tech plan', 'plan the implementation', 'how should we build', 'what's the approach for', 'break this down', or when a brainstorm/requirements document is ready for technical planning. Best when requirements are at least roughly defined; for exploratory or ambiguous requests, prefer ce:brainstorm first."
-argument-hint: "[optional: feature description, requirements doc path, or improvement idea]"
+description: "Transform feature descriptions or requirements into structured implementation plans grounded in repo patterns and research. Also deepen existing plans with interactive review of sub-agent findings. Use for plan creation when the user says 'plan this', 'create a plan', 'write a tech plan', 'plan the implementation', 'how should we build', 'what's the approach for', 'break this down', or when a brainstorm/requirements document is ready for technical planning. Use for plan deepening when the user says 'deepen the plan', 'deepen my plan', 'deepening pass', or uses 'deepen' in reference to a plan. Best when requirements are at least roughly defined; for exploratory or ambiguous requests, prefer ce:brainstorm first."
+argument-hint: "[optional: feature description, requirements doc path, plan path to deepen, or improvement idea]"
 ---
 
 # Create Technical Plan
@@ -61,9 +61,13 @@ If the user references an existing plan file or there is an obvious recent match
 - Confirm whether to update it in place or create a new plan
 - If updating, preserve completed checkboxes and revise only the still-relevant sections
 
-**Re-deepen fast path:** If the plan appears complete (all major sections present, implementation units defined, `status: active`) and the user's request is specifically about deepening or strengthening the plan — detected by signal words like "deepen", "strengthen", "confidence", "gaps", or an explicit request to re-deepen — short-circuit directly to Phase 5.3 (Confidence Check and Deepening). This avoids re-running the full planning workflow just to evaluate deepening.
+**Deepen intent:** The word "deepen" (or "deepening") in reference to a plan is the primary trigger for the deepening fast path. When the user says "deepen the plan", "deepen my plan", "run a deepening pass", or similar, the target document is a **plan** in `docs/plans/`, not a requirements document. Use any path, keyword, or context the user provides to identify the right plan. If a path is provided, verify it is actually a plan document. If the match is not obvious, confirm with the user before proceeding.
 
-Normal editing requests (e.g., "update the test scenarios", "add a new implementation unit") should NOT trigger the fast path — they follow the standard resume flow.
+Words like "strengthen", "confidence", "gaps", and "rigor" are NOT sufficient on their own to trigger deepening. These words appear in normal editing requests ("strengthen that section about the diagram", "there are gaps in the test scenarios") and should not cause a holistic deepening pass. Only treat them as deepening intent when the request clearly targets the plan as a whole and does not name a specific section or content area to change — and even then, prefer to confirm with the user before entering the deepening flow.
+
+Once the plan is identified and appears complete (all major sections present, implementation units defined, `status: active`), short-circuit to Phase 5.3 (Confidence Check and Deepening) in **interactive mode**. This avoids re-running the full planning workflow and gives the user control over which findings are integrated.
+
+Normal editing requests (e.g., "update the test scenarios", "add a new implementation unit", "strengthen the risk section") should NOT trigger the fast path — they follow the standard resume flow.
 
 If the plan already has a `deepened: YYYY-MM-DD` frontmatter field and there is no explicit user request to re-deepen, the fast path still applies the same confidence-gap evaluation — it does not force deepening.
 
@@ -653,13 +657,20 @@ Plan written to docs/plans/[filename]
 
 #### 5.3 Confidence Check and Deepening
 
-After writing the plan file, automatically evaluate whether the plan needs strengthening. This phase runs without asking the user for approval. The user sees what is being strengthened but does not need to make a decision.
+After writing the plan file, automatically evaluate whether the plan needs strengthening.
+
+**Two deepening modes:**
+
+- **Auto mode** (default during plan generation): Runs without asking the user for approval. The user sees what is being strengthened but does not need to make a decision. Sub-agent findings are synthesized directly into the plan.
+- **Interactive mode** (activated by the re-deepen fast path in Phase 0.1): The user explicitly asked to deepen an existing plan. Sub-agent findings are presented individually for review before integration. The user can accept, reject, or discuss each agent's findings. Only accepted findings are synthesized into the plan.
+
+Interactive mode exists because on-demand deepening is a different user posture — the user already has a plan they are invested in and wants to be surgical about what changes. This applies whether the plan was generated by this skill, written by hand, or produced by another tool.
 
 `document-review` and this confidence check are different:
 - Use the `document-review` skill when the document needs clarity, simplification, completeness, or scope control
 - This confidence check strengthens rationale, sequencing, risk treatment, and system-wide thinking when the plan is structurally sound but still needs stronger grounding
 
-**Pipeline mode:** This phase runs in pipeline/disable-model-invocation mode using the same gate logic described below. No user interaction needed.
+**Pipeline mode:** This phase always runs in auto mode in pipeline/disable-model-invocation contexts. No user interaction needed.
 
 ##### 5.3.1 Classify Plan Depth and Topic Risk
 
@@ -868,10 +879,35 @@ If agent outputs conflict:
 - Prefer official framework documentation over secondary best-practice summaries when the conflict is about library behavior
 - If a real tradeoff remains, record it explicitly in the plan
 
+##### 5.3.6b Interactive Finding Review (Interactive Mode Only)
+
+Skip this step in auto mode — proceed directly to 5.3.7.
+
+In interactive mode, present each agent's findings to the user before integration. For each agent that returned findings:
+
+1. **Summarize the agent and its target section** — e.g., "The architecture-strategist reviewed Key Technical Decisions and found:"
+2. **Present the findings concisely** — bullet the key points, not the raw agent output. Include enough context for the user to evaluate: what the agent found, what evidence supports it, and what plan change it implies.
+3. **Ask the user** using the platform's blocking question tool when available (see Interaction Method):
+   - **Accept** — integrate these findings into the plan
+   - **Reject** — discard these findings entirely
+   - **Discuss** — the user wants to talk through the findings before deciding
+
+If the user chooses "Discuss", engage in brief dialogue about the findings and then re-ask with only accept/reject (no discuss option on the second ask). The user makes a deliberate choice either way.
+
+When presenting findings from multiple agents targeting the same section, present them one agent at a time so the user can make independent decisions. Do not merge findings from different agents before showing them.
+
+After all agents have been reviewed, carry only the accepted findings forward to 5.3.7.
+
+If the user accepted no findings, report "No findings accepted — plan unchanged." If artifact-backed mode was used, clean up the scratch directory before continuing. Then proceed directly to Phase 5.4 (skip document-review and synthesis — the plan was not modified).
+
+If findings were accepted and the plan was modified, proceed through 5.3.7 and 5.3.8 as normal — document-review acts as a quality gate on the changes.
+
 ##### 5.3.7 Synthesize and Update the Plan
 
 Strengthen only the selected sections. Keep the plan coherent and preserve its overall structure.
 
+**In interactive mode:** Only integrate findings the user accepted in 5.3.6b. If some findings from different agents touch the same section, reconcile them coherently but do not reintroduce rejected findings.
+
 Allowed changes:
 - Clarify or strengthen decision rationale
 - Tighten requirements trace or origin fidelity
PATCH

echo "Gold patch applied."
