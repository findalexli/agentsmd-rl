#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "5. **Amend or create a follow-up commit when the check produces edits.** If step" "plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md" && grep -qF "c. In full mode, explain to the user why this matters \u2014 agents working in this r" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md b/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md
@@ -641,3 +641,39 @@ Write a descriptive commit message that:
 Use **Replace** only when the refresh process has enough real evidence to write a trustworthy successor. When evidence is insufficient, mark as stale and recommend `ce:compound` for when the user next encounters that problem area.
 
 Use **Consolidate** proactively when the document set has grown organically and redundancy has crept in. Every `ce:compound` invocation adds a new doc — over time, multiple docs may cover the same problem from slightly different angles. Periodic consolidation keeps the document set lean and authoritative.
+
+## Discoverability Check
+
+After the refresh report is generated, check whether the project's instruction files would lead an agent to discover and search `docs/solutions/` before starting work in a documented area. This runs every time — the knowledge store only compounds value when agents can find it. If this check produces edits, they are committed as part of (or immediately after) the Phase 5 commit flow — see step 5 below.
+
+1. Identify which root-level instruction files exist (AGENTS.md, CLAUDE.md, or both). Read the file(s) and determine which holds the substantive content — one file may just be a shim that `@`-includes the other (e.g., `CLAUDE.md` containing only `@AGENTS.md`, or vice versa). The substantive file is the assessment and edit target; ignore shims. If neither file exists, skip this check entirely.
+2. Assess whether an agent reading the instruction files would learn three things:
+   - That a searchable knowledge store of documented solutions exists
+   - Enough about its structure to search effectively (category organization, YAML frontmatter fields like `module`, `tags`, `problem_type`)
+   - When to search it (before implementing features, debugging issues, or making decisions in documented areas — learnings may cover bugs, best practices, workflow patterns, or other institutional knowledge)
+
+   This is a semantic assessment, not a string match. The information could be a line in an architecture section, a bullet in a gotchas section, spread across multiple places, or expressed without ever using the exact path `docs/solutions/`. Use judgment — if an agent would reasonably discover and use the knowledge store after reading the file, the check passes.
+
+3. If the spirit is already met, no action needed.
+4. If not:
+   a. Based on the file's existing structure, tone, and density, identify where a mention fits naturally. Before creating a new section, check whether the information could be a single line in the closest related section — an architecture tree, a directory listing, a documentation section, or a conventions block. A line added to an existing section is almost always better than a new headed section. Only add a new section as a last resort when the file has clear sectioned structure and nothing is even remotely related.
+   b. Draft the smallest addition that communicates the three things. Match the file's existing style and density. The addition should describe the knowledge store itself, not the plugin.
+
+      Keep the tone informational, not imperative. Express timing as description, not instruction — "relevant when implementing or debugging in documented areas" rather than "check before implementing or debugging." Imperative directives like "always search before implementing" cause redundant reads when a workflow already includes a dedicated search step. The goal is awareness: agents learn the folder exists and what's in it, then use their own judgment about when to consult it.
+
+      Examples of calibration (not templates — adapt to the file):
+
+      When there's an existing directory listing or architecture section — add a line:
+      ```
+      docs/solutions/  # documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (module, tags, problem_type)
+      ```
+
+      When nothing in the file is a natural fit — a small headed section is appropriate:
+      ```
+      ## Documented Solutions
+
+      `docs/solutions/` — documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`). Relevant when implementing or debugging in documented areas.
+      ```
+   c. In interactive mode, explain to the user why this matters — agents working in this repo (including fresh sessions, other tools, or collaborators without the plugin) won't know to check `docs/solutions/` unless the instruction file surfaces it. Show the proposed change and where it would go, then use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini) to get consent before making the edit. If no question tool is available, present the proposal and wait for the user's reply. In autofix mode, include it as a "Discoverability recommendation" line in the report — do not attempt to edit instruction files (autofix scope is doc maintenance, not project config).
+
+5. **Amend or create a follow-up commit when the check produces edits.** If step 4 resulted in an edit to an instruction file and Phase 5 already committed the refresh changes, stage the newly edited file and either amend the existing commit (if still on the same branch and no push has occurred) or create a small follow-up commit (e.g., `docs: add docs/solutions/ discoverability to AGENTS.md`). If Phase 5 already pushed the branch to a remote (e.g., the branch+PR path), push the follow-up commit as well so the open PR includes the discoverability change. This keeps the working tree clean and the remote in sync at the end of the run. If the user chose "Don't commit" in Phase 5, leave the instruction-file edit unstaged alongside the other uncommitted refresh changes — no separate commit logic needed.
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -41,9 +41,9 @@ Compact-safe mode exists as a lightweight alternative — see the **Compact-Safe
 ### Full Mode
 
 <critical_requirement>
-**Only ONE file gets written - the final documentation.**
+**The primary output is ONE file - the final documentation.**
 
-Phase 1 subagents return TEXT DATA to the orchestrator. They must NOT use Write, Edit, or create any files. Only the orchestrator (Phase 2) writes the final documentation file.
+Phase 1 subagents return TEXT DATA to the orchestrator. They must NOT use Write, Edit, or create any files. Only the orchestrator writes files: the solution doc in Phase 2, and — if the Discoverability Check finds a gap — a small edit to a project instruction file (AGENTS.md or CLAUDE.md). The instruction-file edit is maintenance, not a second deliverable; it ensures future agents can discover the knowledge store.
 </critical_requirement>
 
 ### Phase 0.5: Auto Memory Scan
@@ -218,6 +218,40 @@ Do not invoke `ce:compound-refresh` without an argument unless the user explicit
 
 Always capture the new learning first. Refresh is a targeted maintenance follow-up, not a prerequisite for documentation.
 
+### Discoverability Check
+
+After the learning is written and the refresh decision is made, check whether the project's instruction files would lead an agent to discover and search `docs/solutions/` before starting work in a documented area. This runs every time — the knowledge store only compounds value when agents can find it.
+
+1. Identify which root-level instruction files exist (AGENTS.md, CLAUDE.md, or both). Read the file(s) and determine which holds the substantive content — one file may just be a shim that `@`-includes the other (e.g., `CLAUDE.md` containing only `@AGENTS.md`, or vice versa). The substantive file is the assessment and edit target; ignore shims. If neither file exists, skip this check entirely.
+2. Assess whether an agent reading the instruction files would learn three things:
+   - That a searchable knowledge store of documented solutions exists
+   - Enough about its structure to search effectively (category organization, YAML frontmatter fields like `module`, `tags`, `problem_type`)
+   - When to search it (before implementing features, debugging issues, or making decisions in documented areas — learnings may cover bugs, best practices, workflow patterns, or other institutional knowledge)
+
+   This is a semantic assessment, not a string match. The information could be a line in an architecture section, a bullet in a gotchas section, spread across multiple places, or expressed without ever using the exact path `docs/solutions/`. Use judgment — if an agent would reasonably discover and use the knowledge store after reading the file, the check passes.
+
+3. If the spirit is already met, no action needed — move on.
+4. If not:
+   a. Based on the file's existing structure, tone, and density, identify where a mention fits naturally. Before creating a new section, check whether the information could be a single line in the closest related section — an architecture tree, a directory listing, a documentation section, or a conventions block. A line added to an existing section is almost always better than a new headed section. Only add a new section as a last resort when the file has clear sectioned structure and nothing is even remotely related.
+   b. Draft the smallest addition that communicates the three things. Match the file's existing style and density. The addition should describe the knowledge store itself, not the plugin — an agent without the plugin should still find value in it.
+
+      Keep the tone informational, not imperative. Express timing as description, not instruction — "relevant when implementing or debugging in documented areas" rather than "check before implementing or debugging." Imperative directives like "always search before implementing" cause redundant reads when a workflow already includes a dedicated search step. The goal is awareness: agents learn the folder exists and what's in it, then use their own judgment about when to consult it.
+
+      Examples of calibration (not templates — adapt to the file):
+
+      When there's an existing directory listing or architecture section — add a line:
+      ```
+      docs/solutions/  # documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (module, tags, problem_type)
+      ```
+
+      When nothing in the file is a natural fit — a small headed section is appropriate:
+      ```
+      ## Documented Solutions
+
+      `docs/solutions/` — documented solutions to past problems (bugs, best practices, workflow patterns), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`). Relevant when implementing or debugging in documented areas.
+      ```
+   c. In full mode, explain to the user why this matters — agents working in this repo (including fresh sessions, other tools, or collaborators without the plugin) won't know to check `docs/solutions/` unless the instruction file surfaces it. Show the proposed change and where it would go, then use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini) to get consent before making the edit. If no question tool is available, present the proposal and wait for the user's reply. In compact-safe mode, output a one-liner note and move on
+
 ### Phase 3: Optional Enhancement
 
 **WAIT for Phase 2 to complete before proceeding.**
@@ -261,6 +295,10 @@ The orchestrator (main conversation) performs ALL of the following in one sequen
 File created:
 - docs/solutions/[category]/[filename].md
 
+[If discoverability check found instruction files don't surface the knowledge store:]
+Tip: Your AGENTS.md/CLAUDE.md doesn't surface docs/solutions/ to agents —
+a brief mention helps all agents discover these learnings.
+
 Note: This was created in compact-safe mode. For richer documentation
 (cross-references, detailed prevention strategies, specialized reviews),
 re-run /compound in a fresh session.
@@ -319,7 +357,7 @@ In compact-safe mode, the overlap check is skipped (no Related Docs Finder subag
 |----------|-----------|
 | Subagents write files like `context-analysis.md`, `solution-draft.md` | Subagents return text data; orchestrator writes one final file |
 | Research and assembly run in parallel | Research completes → then assembly runs |
-| Multiple files created during workflow | One file written or updated: `docs/solutions/[category]/[filename].md` |
+| Multiple files created during workflow | One solution doc written or updated: `docs/solutions/[category]/[filename].md` (plus an optional small edit to a project instruction file for discoverability) |
 | Creating a new doc when an existing doc covers the same problem | Check overlap assessment; update the existing doc when overlap is high |
 
 ## Success Output
PATCH

echo "Gold patch applied."
