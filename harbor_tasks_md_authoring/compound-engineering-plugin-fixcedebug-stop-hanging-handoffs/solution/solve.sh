#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "**If Phase 3 ran**, immediately after the summary prompt the user for the next a" "plugins/compound-engineering/skills/ce-debug/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-debug/SKILL.md b/plugins/compound-engineering/skills/ce-debug/SKILL.md
@@ -27,7 +27,7 @@ These principles govern every phase. They are repeated at decision points becaus
 | 1 | Investigate | Reproduce the bug, trace the code path |
 | 2 | Root Cause | Form hypotheses with predictions for uncertain links, test them, **causal chain gate**, smart escalation |
 | 3 | Fix | Only if user chose to fix. Test-first fix with workspace safety checks |
-| 4 | Close | Structured summary, handoff options |
+| 4 | Handoff | Structured summary, then prompt the user for the next action |
 
 All phases self-size — a simple bug flows through them in seconds, a complex bug spends more time in each naturally. No complexity classification, no phase skipping.
 
@@ -39,9 +39,9 @@ Parse the input and reach a clear problem statement.
 
 **If the input references an issue tracker**, fetch it:
 - GitHub (`#123`, `org/repo#123`, github.com URL): Parse the issue reference from `<bug_description>` and fetch with `gh issue view <number> --json title,body,comments,labels`. For URLs, pass the URL directly to `gh`.
-- Other trackers (Linear URL/ID, Jira URL/key, any tracker URL): Attempt to fetch using available MCP tools or by fetching the URL content. If the fetch fails — auth, missing tool, non-public page — ask the user to paste the relevant issue content.
+- Other trackers (Linear URL/ID, Jira URL/key, any tracker URL): Attempt to fetch using available MCP tools or by fetching the URL content. If the fetch fails — auth, missing tool, non-public page — ask the user to paste the relevant issue content. Ensure the fetch includes the full comment thread, not just the opening description.
 
-Extract reported symptoms, expected behavior, reproduction steps, and environment details. Then proceed to Phase 1.
+Read the full conversation — the original description AND every comment, with particular attention to the latest ones. Comments frequently contain updated reproduction steps, narrowed scope, prior failed attempts, additional stack traces, or a pivot to a different suspected root cause; treating the opening post as the whole picture often sends the investigation in the wrong direction. Extract reported symptoms, expected behavior, reproduction steps, and environment details from the combined thread. Then proceed to Phase 1.
 
 **Everything else** (stack traces, test paths, error messages, descriptions of broken behavior): Proceed directly to Phase 1.
 
@@ -113,10 +113,14 @@ Once the root cause is confirmed, present:
 - Which tests to add or modify to prevent recurrence (specific test file, test case description, what the assertion should verify)
 - Whether existing tests should have caught this and why they did not
 
-Then offer next steps using the platform's blocking question tool: `AskUserQuestion` in Claude Code (call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded), `request_user_input` in Codex, `ask_user` in Gemini. Fall back to numbered options in chat only when no blocking tool exists in the harness or the call errors (e.g., Codex edit modes) — not because a schema load is required. Never silently skip the question:
+Then offer next steps.
+
+Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded — a pending schema load is not a reason to fall back. Fall back to numbered options in chat only when no blocking tool exists in the harness or the call errors (e.g., Codex edit modes). Never silently skip the question.
+
+Options to offer:
 
 1. **Fix it now** — proceed to Phase 3
-2. **View in Proof** (`/ce-proof`) — for easy review and sharing with others
+2. **Diagnosis only — I'll take it from here** — skip the fix, proceed to Phase 4's summary, and end the skill
 3. **Rethink the design** (`/ce-brainstorm`) — only when the root cause reveals a design problem (see below)
 
 Do not assume the user wants action right now. The test recommendations are part of the diagnosis regardless of which path is chosen.
@@ -148,7 +152,7 @@ Present the diagnosis to the user before proceeding.
 
 *Reminder: one change at a time. If you are changing multiple things, stop.*
 
-If the user chose Proof or brainstorm at the end of Phase 2, skip this phase — the skill's job was the diagnosis.
+If the user chose "Diagnosis only" at the end of Phase 2, skip this phase and go straight to Phase 4 for the summary — the skill's job was the diagnosis. If they chose "Rethink the design", control has transferred to `/ce-brainstorm` and this skill ends.
 
 **Workspace check:** Before editing files, check for uncommitted changes (`git status`). If the user has unstaged work in files that need modification, confirm before editing — do not overwrite in-progress changes.
 
@@ -169,9 +173,9 @@ How was this introduced? What allowed it to survive? If a systemic gap was found
 
 ---
 
-### Phase 4: Close
+### Phase 4: Handoff
 
-**Structured summary:**
+**Structured summary** — always write this first:
 
 ```
 ## Debug Summary
@@ -183,9 +187,12 @@ How was this introduced? What allowed it to survive? If a systemic gap was found
 **Confidence**: [High/Medium/Low]
 ```
 
-**Handoff options** (use platform question tool, or present numbered options and wait):
-1. Commit the fix (if Phase 3 ran)
-2. Document as a learning (`/ce-compound`)
-3. Post findings to the issue (if entry came from an issue tracker) — convey: confirmed root cause, verified reproduction steps, relevant code references, and suggested fix direction; keep it concise and useful for whoever picks up the issue next
-4. View in Proof (`/ce-proof`) — for easy review and sharing with others
-5. Done
+**If Phase 3 was skipped** (user chose "Diagnosis only" in Phase 2), stop after the summary — the user already told you they were taking it from here. Do not prompt.
+
+**If Phase 3 ran**, immediately after the summary prompt the user for the next action via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded — a pending schema load is not a reason to fall back. Fall back to numbered options in chat only when no blocking tool exists in the harness or the call errors (e.g., Codex edit modes). Never end the phase without collecting a response — do not stop at "ready when you are" or any other passive phrasing that leaves the user hanging.
+
+Options (include only those that apply):
+
+1. **Commit the fix** — stage and commit the change (always applies here, since Phase 3 ran)
+2. **Document as a learning** (`/ce-compound`) — capture the bug and fix as a reusable pattern
+3. **Post findings to the issue** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came from an issue tracker)
PATCH

echo "Gold patch applied."
