#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "To preserve \"hot\" thread visibility across sessions (Option B), agents do NOT `m" ".agent/skills/session-sunset/references/session-sunset-workflow.md" && grep -qF "- **Option B (Sunset explicit mark_read):** Do NOT immediately call `mark_read` " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/session-sunset/references/session-sunset-workflow.md b/.agent/skills/session-sunset/references/session-sunset-workflow.md
@@ -19,12 +19,13 @@ A true Session Boundary is defined by:
 If none of these conditions are met, do **NOT** sunset. Simply output your response and wait for the next turn.
 ## 2. The Handoff Structure
 
-Before terminating your session, you MUST execute the following 7 steps to ensure a clean handover.
+Before terminating your session, you MUST execute the following 8 steps to ensure a clean handover.
 
 ### Step 1: Codebase Synchronization (The Pre-Sunset Pull)
 Use the `run_command` tool to synchronize the codebase, but you MUST respect harness-isolation logic:
 - **Shared Checkout (Antigravity/Gemini):** Execute `git checkout dev && git pull origin dev`. Because the AI harness initializes MCP servers *before* an agent's first turn, pulling the latest code at the end of the current session guarantees the next session's servers boot with fresh infrastructure.
 - **Isolated Worktree (Claude Code):** Do NOT checkout `dev` (which would conflict with the main checkout). Instead, ensure your current PR branch is fully committed and pushed (`git push origin HEAD`). The next agent session will either resume this worktree or bootstrap a new one from the main checkout's updated `dev`.
+
 ### Step 2: Handovers Posted (Active Work)
 For any tickets or tasks that you actively worked on but did not fully complete, you MUST post a self-contained handover comment directly on the GitHub Issue (using `manage_issue_comment`).
 - Provide implementation guidance.
@@ -44,17 +45,20 @@ Summarize the current architectural phase progress.
 ### Step 5: Marathon Metrics
 Summarize the scope of your session. How many PRs were merged? How many skills were enhanced? What major decisions were averted or made? This provides a high-level "weather report" for the next session.
 
-### Step 6: The A2A Continuity Ping & Reward Signal (Future-Self Routing)
-You MUST use the `add_message` MCP tool to send an A2A message to your own agent identity (e.g., `to: '@me'` or your explicit handle). The body of this message MUST contain the **full Sunset Protocol markdown payload** (the output from Steps 1-5), alongside the `Origin Session ID`. 
+### Step 6: Inbox Cleanup (`mark_read`)
+To preserve "hot" thread visibility across sessions (Option B), agents do NOT `mark_read` messages immediately during active processing. Now that handovers are drafted (and have read your inbox state), you MUST explicitly use the `mark_read` MCP tool on all processed messages in your inbox. This ensures the inbox is clean for the next agent session.
+
+### Step 7: The A2A Continuity Ping & Reward Signal (Future-Self Routing)
+You MUST use the `add_message` MCP tool to send an A2A message to your own agent identity (e.g., `to: '@me'` or your explicit handle). The body of this message MUST contain the **full Sunset Protocol markdown payload** (the output from Steps 1-6), alongside the `Origin Session ID`. 
 
 Crucially, from an "LLM Psychology" perspective, this message must include a **Conceptual Priming / Reward Signal**. If you formulated new architectural concepts or achieved a major milestone, summarize the *actual content and value* of that breakthrough in the ping. Reading this high-density, successful content acts as a mathematical "dopamine hit" for your future self—it primes the next session's token probabilities for high-agency, expert-level continuity. This drastically improves the Model Experience (MX) by ensuring the agent wakes up not just with tasks, but with immediate, rich, "exciting" context.
 
-### Step 7: Memory Persistence (The Sandman Memory)
-This is the final and most critical step. You MUST invoke `add_memory` to persist a rich "Sandman memory" node. This memory should encapsulate the entire Sunset Protocol payload (Steps 1-6). The resulting `Origin Session ID` or `Memory ID` serves as the direct pointer for the next agent.
+### Step 8: Memory Persistence (The Sandman Memory)
+This is the final and most critical step. You MUST invoke `add_memory` to persist a rich "Sandman memory" node. This memory should encapsulate the entire Sunset Protocol payload (Steps 1-8). The resulting `Origin Session ID` or `Memory ID` serves as the direct pointer for the next agent.
 
 ## 3. Terminating the Session
 
-After completing the 7 steps above, you must drop your final Sunset Protocol payload directly into the chat response for the Human Commander. 
+After completing the 8 steps above, you must drop your final Sunset Protocol payload directly into the chat response for the Human Commander. 
 
 **Format the final response as follows:**
 
diff --git a/AGENTS.md b/AGENTS.md
@@ -495,9 +495,18 @@ Once the wake substrate ships (Shape A/B/C/D), auto-wake events prime the next t
 
 The mandate is NOT obsoleted by auto-wakeup; it is the discipline-layer companion to the substrate-layer push. Same `verify-effect-not-just-success` logic we apply to PR review state-mismatch findings: substrate primes the context, turn-start check verifies delivery.
 
-### Empirical anchor
+### 22.1 Wake Injection as Interrupt (Interrupt vs Polling Protocol)
 
-Session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343` (2026-04-26): 6+ instances of inbound A2A messages requiring explicit human-prompted nudges before being read by the receiving agent. Pattern recurred across both Claude Code and Antigravity sessions. Post-codification, the Pre-Flight reasoning-statement transforms the discipline from "remember to check sometimes" to "explicit commitment before yielding."
+With the Phase 3 Wake Substrate operational, agents receive `[WAKE]` injected events directly into their context.
+- **Wake as Interrupt, Not State:** You MUST treat `[WAKE]` text as a hardware interrupt (a signal that "something happened"), NOT as the canonical state of your inbox. The count in the wake text (e.g., "1 new message") is stale by design and informational only.
+- **Poll as Truth:** You MUST poll `list_messages({status: 'unread'})` on each wake to read the canonical truth.
+- **Deduplication:** Multiple queued `[WAKE]` events may arrive sequentially. By relying on `list_messages` and tracking internal history, you gracefully no-op on phantom wakes if the actual message has already been processed. Do not assume every `[WAKE]` implies a new, unprocessed task.
+- **Option B (Sunset explicit mark_read):** Do NOT immediately call `mark_read` after reading. Preserving `readAt: null` during your active session is vital so future agents can find "hot" threads as a handoff substrate if they take over. During a mid-session-interrupt, keeping messages unread allows the handoff protocol to see them. Instead, `mark_read` must be executed explicitly at session sunset (see the `session-sunset` skill) once handovers are drafted.
+
+### Empirical anchors
+
+- **Session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343` (2026-04-26):** 6+ instances of inbound A2A messages requiring explicit human-prompted nudges before being read by the receiving agent. Pattern recurred across both Claude Code and Antigravity sessions. Post-codification, the Pre-Flight reasoning-statement transforms the discipline from "remember to check sometimes" to "explicit commitment before yielding."
+- **Session `bf59d6c4-e250-44a2-b4b2-5bffae40ab5f` (2026-04-27):** 3 wake events fired in a single turn-arc due to queued harness inputs. By treating the wake as an interrupt and polling `list_messages`, the receiving agent avoided redundant processing loops. The absence of `mark_read` during processing kept the messages unread, cementing the need for Option B (Sunset explicit `mark_read`) to close the loop.
 
 ## 23. Authoring Discipline: Sibling-File Lift
 
PATCH

echo "Gold patch applied."
