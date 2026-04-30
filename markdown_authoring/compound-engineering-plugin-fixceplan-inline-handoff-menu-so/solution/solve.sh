#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "If the plan already appears sufficiently grounded and the thin-grounding overrid" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -407,6 +407,8 @@ Examples:
 
 ### Phase 4: Write the Plan
 
+**NEVER CODE during this skill.** Research, decide, and write the plan — do not start implementation.
+
 Use one planning philosophy across all depths. Change the amount of detail, not the boundary between planning and execution.
 
 #### 4.1 Plan Depth Guidance
@@ -723,14 +725,28 @@ Build a risk profile. Treat these as high-risk signals:
 - **Deep** or high-risk plans often benefit from a targeted second pass
 - **Thin local grounding override:** If Phase 1.2 triggered external research because local patterns were thin (fewer than 3 direct examples or adjacent-domain match), always proceed to scoring regardless of how grounded the plan appears. When the plan was built on unfamiliar territory, claims about system behavior are more likely to be assumptions than verified facts. The scoring pass is cheap — if the plan is genuinely solid, scoring finds nothing and exits quickly
 
-If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening" and skip to Phase 5.3.8 (Document Review). Document-review always runs regardless of whether deepening was needed — the two tools catch different classes of issues.
+If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening", then **load `references/plan-handoff.md` now and execute 5.3.8 → 5.3.9 → 5.4 in sequence**. Document review is mandatory — do not skip it because the confidence check passed. The two tools catch different classes of issues.
 
 ##### 5.3.3–5.3.7 Deepening Execution
 
 When deepening is warranted, read `references/deepening-workflow.md` for confidence scoring checklists, section-to-agent dispatch mapping, execution mode selection, research execution, interactive finding review, and plan synthesis instructions. Execute steps 5.3.3 through 5.3.7 from that file, then return here for 5.3.8.
 
 ##### 5.3.8–5.4 Document Review, Final Checks, and Post-Generation Options
 
-When reaching this phase, read `references/plan-handoff.md` for document review instructions (5.3.8), final checks and cleanup (5.3.9), post-generation options menu (5.4), and issue creation. Do not load this file earlier. Document review is mandatory — do not skip it even if the confidence check already ran.
+**Load `references/plan-handoff.md` now.** It contains the full instructions for 5.3.8 (document review), 5.3.9 (final checks and cleanup), and 5.4 (post-generation handoff, including the Proof HITL flow, post-HITL re-review, and Issue Creation branching). Document review is mandatory — do not skip it even if the confidence check already ran.
+
+After document review and final checks, present this menu using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the numbered options in chat and wait for the user's reply before proceeding.
+
+**Question:** "Plan ready at `docs/plans/YYYY-MM-DD-NNN-<type>-<name>-plan.md`. What would you like to do next?"
+
+**Options:**
+1. **Start `/ce-work`** (recommended) - Begin implementing this plan in the current session
+2. **Create Issue** - Create a tracked issue from this plan in your configured issue tracker (GitHub or Linear)
+3. **Open in Proof (web app) — review and comment to iterate with the agent** - Open the doc in Every's Proof editor, iterate with the agent via comments, or copy a link to share with others
+4. **Done for now** - Pause; the plan file is saved and can be resumed later
+
+Routing each selection, contextual surfacing of residual document-review findings, and the post-HITL resync logic all live in `references/plan-handoff.md` — follow it for every branch.
+
+**Completion check:** This skill is not complete until the post-generation menu above has been presented and the user has selected an action. If you have written the plan file and have not yet presented the menu, you are not done — go to the load instruction above and continue.
 
-NEVER CODE! Research, decide, and write the plan.
+**Pipeline mode exception:** In LFG, SLFG, or any `disable-model-invocation` context, skip the interactive menu and return control to the caller after the plan file is written, confidence check has run, and `ce-doc-review` has run in headless mode (per `references/plan-handoff.md`).
PATCH

echo "Gold patch applied."
