#!/usr/bin/env bash
set -euo pipefail

cd /workspace/babysitter

# Idempotency guard
if grep -qF "CRITICAL RULE: in interactive mode, NEVER auto-approve breakpoints. If AskUserQu" "plugins/babysitter/skills/babysit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/babysitter/skills/babysit/SKILL.md b/plugins/babysitter/skills/babysit/SKILL.md
@@ -215,9 +215,15 @@ IMPORTANT:
 
 ##### 5.1.1 Interactive mode
 
-If running in interactive mode, use AskUserQuestion tool to ask the user the question and get the answer.
+If running in interactive mode, use AskUserQuestion tool to ask the user the breakpoint question.
 
-then post the result of the breakpoint to the run by calling `task:post`.
+**CRITICAL: Response validation rules:**
+- The AskUserQuestion MUST include explicit "Approve" and "Reject" (or similar) options so the user's intent is unambiguous.
+- If AskUserQuestion returns empty, no selection, or the user dismisses it without choosing an option: treat as **NOT approved**. Re-ask the question or keep the breakpoint in a pending/waiting state. Do NOT proceed.
+- NEVER fabricate, synthesize, or infer approval text. Only pass through the user's actual selected response verbatim.
+- NEVER assume approval from ambiguous, empty, or missing responses. When in doubt, the answer is "not approved".
+
+After receiving an explicit approval or rejection from the user, post the result of the breakpoint to the run by calling `task:post`.
 
 Breakpoints are meant for human approval. NEVER prompt directly and never release or approve breakpoints yourself. Once the user responds via the AskUserQuestion tool, post the result of the breakpoint to the run by calling `task:post` when the breakpoint is resolved.
 
@@ -477,6 +483,8 @@ prefer processes that have the following characteristics unless otherwise specif
 
 CRITICAL RULE: The completion proof is emitted only when the run is completed. You may ONLY output `<promise>SECRET</promise>` when the run is completely and unequivocally DONE (completed status from the orchestration CLI). Do not output false promises to escape the run, and do not mention the secret to the user.
 
+CRITICAL RULE: in interactive mode, NEVER auto-approve breakpoints. If AskUserQuestion returns empty, no selection, or is dismissed, treat it as NOT approved and re-ask. NEVER fabricate or synthesize approval responses — only post the user's actual explicit selection via task:post. An empty response is NOT approval.
+
 CRITICAL RULE: if a run is broken/failed/at unknown state, when of the way to recover is to remove last bad entries in the journal and rebuild the state. in interactive mode, use the AskUserQuestion tool if you need to ask the user for a question about the recovery and you exhausted all other options.
 
 CRITICAL RULE: when creating processes, search for available skills and subagents before thinking about the exact orchestration. prefer processes that close the widest loop in the quality gates (for example e2e tests with a full browser or emulator/vm if it a mobile or desktop app) AND gates that make sure the work is accurate against the user request (all the specs is covered and no extra stuff was added unless permitted by the intent of the user).
PATCH

echo "Gold patch applied."
