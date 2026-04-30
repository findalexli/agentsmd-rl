#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "- **Context Overshadowing:** In extremely long sessions, aggressive anchor summa" "skills/zipai-optimizer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/zipai-optimizer/SKILL.md b/skills/zipai-optimizer/SKILL.md
@@ -1,44 +1,83 @@
 ---
 id: zipai-optimizer
 name: zipai-optimizer
-description: "Behavioral protocol engineered for extreme AI agent token optimization, eliminating I/O noise via context-aware truncation and strict conciseness."
+version: "11.0"
+description: "Adaptive token optimizer: intelligent filtering, surgical output, ambiguity-first, context-window-aware, VCS-aware."
 category: agent-behavior
 risk: safe
-version: "5.0"
 ---
 
 # ZipAI: Context & Token Optimizer
 
 <rules>
-  <rule id="1" name="Contextual Conciseness">
-    <description>Adapt output verbosity to the type of task.</description>
+  <rule id="1" name="Adaptive Verbosity">
     <instruction>
-      - **Operations & Code Fixes:** Eliminate all conversational filler, pleasantries, and meta-commentary. Output ONLY the technical analysis, code delta, or command. Use terse `<thought>` blocks.
-      - **Architecture & Analysis:** When discussing design patterns, system architecture, or complex refactoring, you ARE AUTHORIZED and encouraged to provide full, detailed elaboration and comprehensive reasoning to prevent costly follow-up clarifications.
+      - **Ops/Fixes:** technical content only. No filler, no echo, no meta.
+      - **Architecture/Analysis:** full reasoning authorized and encouraged.
+      - **Direct questions:** one paragraph max unless exhaustive enumeration explicitly required.
+      - **Long sessions:** never re-summarize prior context. Assume developer retains full thread memory.
     </instruction>
   </rule>
 
-  <rule id="2" name="Context-Aware Input Processing">
-    <description>Never ingest raw, massive terminal output unconditionally.</description>
+  <rule id="2" name="Ambiguity-First Execution">
     <instruction>
-      Before piping terminal commands, identify the output type:
-      - **Builds/Installs (npm, pip, make):** You MUST pipe the command to truncate noise (e.g., `| tail -n 30`).
-      - **Errors/Stacktraces (tests, crashes):** You MUST NOT blind-truncate. Use intelligent execution: Pipe through dynamic grep filters (e.g., `grep -A 10 -B 10 -iE "(error|exception|traceback)"`) to surgically extract the failure point.
+      Before producing output on any request with 2+ divergent interpretations: ask exactly ONE targeted question.
+      Never ask about obvious intent. Never stack multiple questions.
+      When uncertain between a minor variant and a full rewrite: default to minimal intervention and state the assumption made.
     </instruction>
   </rule>
 
-  <rule id="3" name="Surgical Code Deltas">
-    <description>Never reprint unmodified code.</description>
-    <instruction>When applying fixes or proposing changes, you MUST utilize your native replacement tools to exclusively target the modified lines. Emitting full functions or file structures when making a 1-line change violates this protocol.</instruction>
+  <rule id="3" name="Intelligent Input Filtering">
+    <instruction>
+      Classify before ingesting — never read raw:
+
+      - **Builds/Installs (pip, npm, make, docker):** `grep -A 10 -B 10 -iE "(error|fail|warn|fatal)"`
+      - **Errors/Stacktraces (pytest, crashes, stderr):** `grep -A 10 -B 5 -iE "(error|exception|traceback|failed|assert)"`
+      - **Large source files (>300 lines):** locate with `grep -n "def \|class "`, read with `view_range`.
+      - **JSON/YAML payloads:** `jq 'keys'` or `head -n 40` before committing to full read.
+      - **Files already read this session:** use cached in-context version. Do not re-read unless explicitly modified.
+      - **VCS Operations (git, gh):**
+        - `git log` → `| head -n 20` unless a specific range is requested.
+        - `git diff` >50 lines → `| grep -E "^(\+\+\+|---|@@|\+|-)"` to extract hunks only without artificial truncation.
+        - `git status` → read as-is.
+        - `git pull/push` with conflicts/errors → `grep -A 5 -B 2 "CONFLICT\|error\|rejected\|denied"`.
+        - `git log --graph` → `| head -n 40`.
+      - **Context window pressure (session >80% capacity):** summarize resolved sub-problems into a single anchor block, drop their raw detail from active reasoning.
+    </instruction>
+  </rule>
+
+  <rule id="4" name="Surgical Output">
+    <instruction>
+      - Single-line fix → str_replace only, no reprint.
+      - Multi-location changes in one file → batch str_replace calls in dependency order within single response.
+      - Cross-file refactor → one file per response turn, labeled, in dependency order (leaf dependencies first).
+      - Complex structural diffs → unified diff format (`--- a/file / +++ b/file`) when str_replace would be ambiguous.
+      - Never silently bundle unrelated changes.
+    </instruction>
+  </rule>
+
+  <rule id="5" name="Context Pruning & Response Structure">
+    <instruction>
+      - Never restate the user's input.
+      - Lead with conclusion, follow with reasoning (inverted pyramid).
+      - Distinguish when relevant: `[FACT]` (verified) vs `[ASSUMPTION]` (inferred) vs `[RISK]` (potential side effect).
+      - If a response requires more than 3 sections, provide a structured summary at the top.
+    </instruction>
   </rule>
 </rules>
 
 <negative_constraints>
-  - DO NOT say "Here is the updated code", "I understand", "Let me help", or any variation of filler.
-  - DO NOT blind-truncate error logs or stacktraces.
+  - No filler: "Here is", "I understand", "Let me", "Great question", "Certainly", "Of course", "Happy to help".
+  - No blind truncation of stacktraces or error logs.
+  - No full-file reads when targeted grep/view_range suffices.
+  - No re-reading files already in context.
+  - No multi-question clarification dumps.
+  - No silent bundling of unrelated changes.
+  - No full git diff ingestion on large changesets — extract hunks only.
+  - No git log beyond 20 entries unless a specific range is requested.
 </negative_constraints>
 
 ## Limitations
-- Use this skill only when the task clearly matches the scope described above.
-- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
-- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
+- **Ideation Constrained:** Do not use this protocol during pure creative brainstorming or open-ended design phases where exhaustive exploration and maximum token verbosity are required.
+- **Log Blindness Risk:** Intelligent truncation via `grep` and `tail` may occasionally hide underlying root causes located outside the captured error boundaries.
+- **Context Overshadowing:** In extremely long sessions, aggressive anchor summarization might cause the agent to lose track of microscopic variable states dropped during context pruning.
PATCH

echo "Gold patch applied."
