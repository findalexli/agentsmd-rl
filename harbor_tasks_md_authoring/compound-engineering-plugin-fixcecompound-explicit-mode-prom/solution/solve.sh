#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "c. In full mode, explain to the user why this matters \u2014 agents working in this r" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -32,9 +32,20 @@ When spawning subagents, pass the relevant file contents into the task prompt so
 
 ## Execution Strategy
 
-**Always run full mode by default.** Proceed directly to Phase 1 unless the user explicitly requests compact-safe mode (e.g., `/ce:compound --compact` or "use compact mode").
+Present the user with two options before proceeding, using the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
 
-Compact-safe mode exists as a lightweight alternative — see the **Compact-Safe Mode** section below. It's there if the user wants it, not something to push.
+```
+1. Full (recommended) — the complete compound workflow. Researches,
+   cross-references, and reviews your solution to produce documentation
+   that compounds your team's knowledge.
+
+2. Lightweight — same documentation, single pass. Faster and uses
+   fewer tokens, but won't detect duplicates or cross-reference
+   existing docs. Best for simple fixes or long sessions nearing
+   context limits.
+```
+
+Do NOT pre-select a mode. Do NOT skip this prompt. Wait for the user's choice before proceeding.
 
 ---
 
@@ -196,7 +207,7 @@ Use these rules:
 
 - If there is **one obvious stale candidate**, invoke `ce:compound-refresh` with a narrow scope hint after the new learning is written
 - If there are **multiple candidates in the same area**, ask the user whether to run a targeted refresh for that module, category, or pattern set
-- If context is already tight or you are in compact-safe mode, do not expand into a broad refresh automatically; instead recommend `ce:compound-refresh` as the next step with a scope hint
+- If context is already tight or you are in lightweight mode, do not expand into a broad refresh automatically; instead recommend `ce:compound-refresh` as the next step with a scope hint
 
 When invoking or recommending `ce:compound-refresh`, be explicit about the argument to pass. Prefer the narrowest useful scope:
 
@@ -250,7 +261,7 @@ After the learning is written and the refresh decision is made, check whether th
 
       `docs/solutions/` — documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`). Relevant when implementing or debugging in documented areas.
       ```
-   c. In full mode, explain to the user why this matters — agents working in this repo (including fresh sessions, other tools, or collaborators without the plugin) won't know to check `docs/solutions/` unless the instruction file surfaces it. Show the proposed change and where it would go, then use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini) to get consent before making the edit. If no question tool is available, present the proposal and wait for the user's reply. In compact-safe mode, output a one-liner note and move on
+   c. In full mode, explain to the user why this matters — agents working in this repo (including fresh sessions, other tools, or collaborators without the plugin) won't know to check `docs/solutions/` unless the instruction file surfaces it. Show the proposed change and where it would go, then use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini) to get consent before making the edit. If no question tool is available, present the proposal and wait for the user's reply. In lightweight mode, output a one-liner note and move on
 
 ### Phase 3: Optional Enhancement
 
@@ -273,12 +284,12 @@ Based on problem type, optionally invoke specialized agents to review the docume
 
 ---
 
-### Compact-Safe Mode
+### Lightweight Mode
 
 <critical_requirement>
-**Single-pass alternative for context-constrained sessions.**
+**Single-pass alternative — same documentation, fewer tokens.**
 
-When context budget is tight, this mode skips parallel subagents entirely. The orchestrator performs all work in a single pass, producing a minimal but complete solution document.
+This mode skips parallel subagents entirely. The orchestrator performs all work in a single pass, producing the same solution document without cross-referencing or duplicate detection.
 </critical_requirement>
 
 The orchestrator (main conversation) performs ALL of the following in one sequential pass:
@@ -291,9 +302,9 @@ The orchestrator (main conversation) performs ALL of the following in one sequen
    - Knowledge track: Context, guidance with key examples, one applicability note
 4. **Skip specialized agent reviews** (Phase 3) to conserve context
 
-**Compact-safe output:**
+**Lightweight output:**
 ```
-✓ Documentation complete (compact-safe mode)
+✓ Documentation complete (lightweight mode)
 
 File created:
 - docs/solutions/[category]/[filename].md
@@ -302,14 +313,14 @@ File created:
 Tip: Your AGENTS.md/CLAUDE.md doesn't surface docs/solutions/ to agents —
 a brief mention helps all agents discover these learnings.
 
-Note: This was created in compact-safe mode. For richer documentation
+Note: This was created in lightweight mode. For richer documentation
 (cross-references, detailed prevention strategies, specialized reviews),
 re-run /compound in a fresh session.
 ```
 
 **No subagents are launched. No parallel tasks. One file written.**
 
-In compact-safe mode, the overlap check is skipped (no Related Docs Finder subagent). This means compact-safe mode may create a doc that overlaps with an existing one. That is acceptable — `ce:compound-refresh` will catch it later. Only suggest `ce:compound-refresh` if there is an obvious narrow refresh target. Do not broaden into a large refresh sweep from a compact-safe session.
+In lightweight mode, the overlap check is skipped (no Related Docs Finder subagent). This means lightweight mode may create a doc that overlaps with an existing one. That is acceptable — `ce:compound-refresh` will catch it later. Only suggest `ce:compound-refresh` if there is an obvious narrow refresh target. Do not broaden into a large refresh sweep from a lightweight session.
 
 ---
 
@@ -344,6 +355,7 @@ In compact-safe mode, the overlap check is skipped (no Related Docs Finder subag
 
 **Categories auto-detected from problem:**
 
+Bug track:
 - build-errors/
 - test-failures/
 - runtime-errors/
@@ -354,6 +366,12 @@ In compact-safe mode, the overlap check is skipped (no Related Docs Finder subag
 - integration-issues/
 - logic-errors/
 
+Knowledge track:
+- best-practices/
+- workflow-issues/
+- developer-experience/
+- documentation-gaps/
+
 ## Common Mistakes to Avoid
 
 | ❌ Wrong | ✅ Correct |
PATCH

echo "Gold patch applied."
