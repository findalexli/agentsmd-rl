#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "> Also scan the \"user's auto-memory\" block injected into your system prompt (Cla" "plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md" && grep -qF "1. **Extract from conversation**: Identify the problem and solution from convers" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md b/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md
@@ -163,7 +163,7 @@ A learning has several dimensions that can independently go stale. Surface-level
 - **Recommended solution** — does the fix still match how the code actually works today? A renamed file with a completely different implementation pattern is not just a path update.
 - **Code examples** — if the learning includes code snippets, do they still reflect the current implementation?
 - **Related docs** — are cross-referenced learnings and patterns still present and consistent?
-- **Auto memory** — does the auto memory directory contain notes in the same problem domain? Read MEMORY.md from the auto memory directory (the path is known from the system prompt context). If it does not exist or is empty, skip this dimension. A memory note describing a different approach than what the learning recommends is a supplementary drift signal.
+- **Auto memory** (Claude Code only) — does the injected auto-memory block in your system prompt contain entries in the same problem domain? Scan that block directly. If the block is absent, skip this dimension. A memory note describing a different approach than what the learning recommends is a supplementary drift signal.
 - **Overlap** — while investigating, note when another doc in scope covers the same problem domain, references the same files, or recommends a similar solution. For each overlap, record: the two file paths, which dimensions overlap (problem, solution, root cause, files, prevention), and which doc appears broader or more current. These signals feed Phase 1.75 (Document-Set Analysis).
 
 Match investigation depth to the learning's specificity — a learning referencing exact file paths and code snippets needs more verification than one describing a general principle.
@@ -274,7 +274,7 @@ Use subagents for context isolation when investigating multiple artifacts — no
 
 > Use dedicated file search and read tools (Glob, Grep, Read) for all investigation. Do NOT use shell commands (ls, find, cat, grep, test, bash) for file operations. This avoids permission prompts and is more reliable.
 >
-> Also read MEMORY.md from the auto memory directory if it exists. Check for notes related to the learning's problem domain. Report any memory-sourced drift signals separately from codebase-sourced evidence, tagged with "(auto memory [claude])" in the evidence section. If MEMORY.md does not exist or is empty, skip this check.
+> Also scan the "user's auto-memory" block injected into your system prompt (Claude Code only). Check for notes related to the learning's problem domain. Report any memory-sourced drift signals separately from codebase-sourced evidence, tagged with "(auto memory [claude])" in the evidence section. If the block is not present in your context, skip this check.
 
 There are two subagent roles:
 
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -69,10 +69,10 @@ Phase 1 subagents return TEXT DATA to the orchestrator. They must NOT use Write,
 
 ### Phase 0.5: Auto Memory Scan
 
-Before launching Phase 1 subagents, check the auto memory directory for notes relevant to the problem being documented.
+Before launching Phase 1 subagents, check the auto-memory block injected into your system prompt for notes relevant to the problem being documented.
 
-1. Read MEMORY.md from the auto memory directory (the path is known from the system prompt context)
-2. If the directory or MEMORY.md does not exist, is empty, or is unreadable, skip this step and proceed to Phase 1 unchanged
+1. Look for a block labeled "user's auto-memory" (Claude Code only) already present in your system prompt context — MEMORY.md's entries are inlined there
+2. If the block is absent, empty, or this is a non-Claude-Code platform, skip this step and proceed to Phase 1 unchanged
 3. Scan the entries for anything related to the problem being documented -- use semantic judgment, not keyword matching
 4. If relevant entries are found, prepare a labeled excerpt block:
 
@@ -337,7 +337,7 @@ This mode skips parallel subagents entirely. The orchestrator performs all work
 
 The orchestrator (main conversation) performs ALL of the following in one sequential pass:
 
-1. **Extract from conversation**: Identify the problem and solution from conversation history. Also read MEMORY.md from the auto memory directory if it exists -- use any relevant notes as supplementary context alongside conversation history. Tag any memory-sourced content incorporated into the final doc with "(auto memory [claude])"
+1. **Extract from conversation**: Identify the problem and solution from conversation history. Also scan the "user's auto-memory" block injected into your system prompt, if present (Claude Code only) -- use any relevant notes as supplementary context alongside conversation history. Tag any memory-sourced content incorporated into the final doc with "(auto memory [claude])"
 2. **Classify**: Read `references/schema.yaml` and `references/yaml-schema.md`, then determine track (bug vs knowledge), category, and filename
 3. **Write minimal doc**: Create `docs/solutions/[category]/[filename].md` using the appropriate track template from `assets/resolution-template.md`, with:
    - YAML frontmatter with track-appropriate fields
PATCH

echo "Gold patch applied."
