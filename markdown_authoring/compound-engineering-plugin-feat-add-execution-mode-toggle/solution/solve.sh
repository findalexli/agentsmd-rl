#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Scratch Space:** When authoring or editing skills and agents that need repo-" "AGENTS.md" && grep -qF "3. **Prefer the simplest execution mode** - Use direct agent synthesis by defaul" "plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md" && grep -qF "- Require each resolver agent to return a short status summary to the parent: co" "plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md" && grep -qF "If the todo set is large enough that even batched short returns are likely to ge" "plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -24,6 +24,7 @@ bun run release:validate  # check plugin/marketplace consistency
 - **Testing:** Run `bun test` after changes that affect parsing, conversion, or output.
 - **Release versioning:** Releases are prepared by release automation, not normal feature PRs. The repo now has multiple release components (`cli`, `compound-engineering`, `coding-tutor`, `marketplace`). GitHub release PRs and GitHub Releases are the canonical release-notes surface for new releases; root `CHANGELOG.md` is only a pointer to that history. Use conventional titles such as `feat:` and `fix:` so release automation can classify change intent, but do not hand-bump release-owned versions or hand-author release notes in routine PRs.
 - **Output Paths:** Keep OpenCode output at `opencode.json` and `.opencode/{agents,skills,plugins}`. For OpenCode, command go to `~/.config/opencode/commands/<name>.md`; `opencode.json` is deep-merged (never overwritten wholesale).
+- **Scratch Space:** When authoring or editing skills and agents that need repo-local scratch space, instruct them to use `.context/` for ephemeral collaboration artifacts. Namespace compound-engineering workflow state under `.context/compound-engineering/<workflow-or-skill-name>/`, add a per-run subdirectory when concurrent runs are plausible, and clean scratch artifacts up after successful completion unless the user asked to inspect them or another agent still needs them. Durable outputs like plans, specs, learnings, and docs do not belong in `.context/`.
 - **ASCII-first:** Use ASCII unless the file already contains Unicode.
 
 ## Directory Layout
diff --git a/plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md b/plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md
@@ -41,10 +41,11 @@ Do not proceed until you have a valid plan file path.
 
 1. **Stress-test, do not inflate** - Deepening should increase justified confidence, not make the plan longer for its own sake.
 2. **Selective depth only** - Focus on the weakest 2-5 sections rather than enriching everything.
-3. **Preserve the planning boundary** - No implementation code, no git command choreography, no exact test command recipes.
-4. **Use artifact-contained evidence** - Work from the written plan, its `Context & Research`, `Sources & References`, and its origin document when present.
-5. **Respect product boundaries** - Do not invent new product requirements. If deepening reveals a product-level gap, surface it as an open question or route back to `ce:brainstorm`.
-6. **Prioritize risk and cross-cutting impact** - The more dangerous or interconnected the work, the more valuable another planning pass becomes.
+3. **Prefer the simplest execution mode** - Use direct agent synthesis by default. Switch to artifact-backed research only when the selected research scope is large enough that returning all findings inline would create avoidable context pressure.
+4. **Preserve the planning boundary** - No implementation code, no git command choreography, no exact test command recipes.
+5. **Use artifact-contained evidence** - Work from the written plan, its `Context & Research`, `Sources & References`, and its origin document when present.
+6. **Respect product boundaries** - Do not invent new product requirements. If deepening reveals a product-level gap, surface it as an open question or route back to `ce:brainstorm`.
+7. **Prioritize risk and cross-cutting impact** - The more dangerous or interconnected the work, the more valuable another planning pass becomes.
 
 ## Workflow
 
@@ -262,14 +263,70 @@ Instruct the agent to return:
 - no implementation code
 - no shell commands
 
+#### 3.3 Choose Research Execution Mode
+
+Use the lightest mode that will work:
+
+- **Direct mode** - Default. Use when the selected section set is small and the parent can safely read the agent outputs inline.
+- **Artifact-backed mode** - Use only when the selected research scope is large enough that inline returns would create unnecessary context pressure.
+
+Signals that justify artifact-backed mode:
+- More than 5 agents are likely to return meaningful findings
+- The selected section excerpts are long enough that repeating them in multiple agent outputs would be wasteful
+- The topic is high-risk and likely to attract bulky source-backed analysis
+- The platform has a history of parent-context instability on large parallel returns
+
+If artifact-backed mode is not clearly warranted, stay in direct mode.
+
 ### Phase 4: Run Targeted Research and Review
 
-Launch the selected agents in parallel.
+Launch the selected agents in parallel using the execution mode chosen in Step 3.3. If the current platform does not support parallel dispatch, run them sequentially instead.
 
 Prefer local repo and institutional evidence first. Use external research only when the gap cannot be closed responsibly from repo context or already-cited sources.
 
 If a selected section can be improved by reading the origin document more carefully, do that before dispatching external agents.
 
+#### 4.1 Direct Mode
+
+Have each selected agent return its findings directly to the parent.
+
+Keep the return payload focused:
+- strongest findings only
+- the evidence or sources that matter
+- the concrete planning improvement implied by the finding
+
+If a direct-mode agent starts producing bulky or repetitive output, stop and switch the remaining research to artifact-backed mode instead of letting the parent context bloat.
+
+#### 4.2 Artifact-Backed Mode
+
+Use a per-run scratch directory under `.context/compound-engineering/deepen-plan-beta/`, for example `.context/compound-engineering/deepen-plan-beta/<run-id>/` or `.context/compound-engineering/deepen-plan-beta/<plan-filename-stem>/`.
+
+Use the scratch directory only for the current deepening pass.
+
+For each selected agent:
+- give it the same plan summary, section text, trigger rationale, depth, and risk profile described in Step 3.2
+- instruct it to write one compact artifact file for its assigned section or sections
+- have it return only a short completion summary to the parent
+
+Prefer a compact markdown artifact unless machine-readable structure is clearly useful. Each artifact should contain:
+- target section id and title
+- why the section was selected
+- 3-7 findings that materially improve planning quality
+- source-backed rationale, including whether the evidence came from repo context, origin context, institutional learnings, official docs, or external best practices
+- the specific plan change implied by each finding
+- any unresolved tradeoff that should remain explicit in the plan
+
+Artifact rules:
+- no implementation code
+- no shell commands
+- no checkpoint logs or self-diagnostics
+- no duplicated boilerplate across files
+- no judge or merge sub-pipeline
+
+Before synthesis:
+- quickly verify that each selected section has at least one usable artifact
+- if an artifact is missing or clearly malformed, re-run that agent or fall back to direct-mode reasoning for that section instead of building a validation pipeline
+
 If agent outputs conflict:
 - Prefer repo-grounded and origin-grounded evidence over generic advice
 - Prefer official framework documentation over secondary best-practice summaries when the conflict is about library behavior
@@ -279,6 +336,12 @@ If agent outputs conflict:
 
 Strengthen only the selected sections. Keep the plan coherent and preserve its overall structure.
 
+If artifact-backed mode was used:
+- read the plan, origin document if present, and the selected section artifacts
+- also incorporate any findings already returned inline from direct-mode agents before a mid-run switch, so early results are not silently dropped
+- synthesize in one pass
+- do not create a separate judge, merge, or quality-review phase unless the user explicitly asks for another pass
+
 Allowed changes:
 - Clarify or strengthen decision rationale
 - Tighten requirements trace or origin fidelity
@@ -311,12 +374,17 @@ Before writing:
 - Confirm the selected sections were actually the weakest ones
 - Confirm origin decisions were preserved when an origin document exists
 - Confirm the final plan still feels right-sized for its depth
+- If artifact-backed mode was used, confirm the scratch artifacts did not become a second hidden plan format
 
 Update the plan file in place by default.
 
 If the user explicitly requests a separate file, append `-deepened` before `.md`, for example:
 - `docs/plans/2026-03-15-001-feat-example-plan-deepened.md`
 
+If artifact-backed mode was used and the user did not ask to inspect the scratch files:
+- clean up the temporary scratch directory after the plan is safely written
+- if cleanup is not practical on the current platform, say where the artifacts were left and that they are temporary workflow output
+
 ## Post-Enhancement Options
 
 If substantive changes were made, present next steps using the platform's blocking question tool when available (see Interaction Method). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.
diff --git a/plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md b/plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md
@@ -49,6 +49,16 @@ Spawn a `compound-engineering:workflow:pr-comment-resolver` agent for each unres
 
 If there are 3 comments, spawn 3 agents — one per comment. Prefer running all agents in parallel; if the platform does not support parallel dispatch, run them sequentially.
 
+Keep parent-context pressure bounded:
+- If there are 1-4 unresolved items, direct parallel returns are fine
+- If there are 5+ unresolved items, launch in batches of at most 4 agents at a time
+- Require each resolver agent to return a short status summary to the parent: comment/thread handled, files changed, tests run or skipped, any blocker that still needs human attention, and for question-only threads the substantive reply text so the parent can post or verify it
+
+If the PR is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-pr-parallel/<run-id>/`:
+- Have each resolver write a compact artifact for its thread there
+- Return only a completion summary to the parent
+- Re-read only the artifacts that are needed to resolve threads, answer reviewer questions, or summarize the batch
+
 ### 4. Commit & Resolve
 
 - Commit changes with a clear message referencing the PR feedback
@@ -70,6 +80,8 @@ bash scripts/get-pr-comments PR_NUMBER
 
 Should return an empty array `[]`. If threads remain, repeat from step 1.
 
+If a scratch directory was used and the user did not ask to inspect it, clean it up after verification succeeds.
+
 ## Scripts
 
 - [scripts/get-pr-comments](scripts/get-pr-comments) - GraphQL query for unresolved review threads
diff --git a/plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md b/plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md
@@ -24,6 +24,16 @@ Spawn a `compound-engineering:workflow:pr-comment-resolver` agent for each unres
 
 If there are 3 items, spawn 3 agents — one per item. Prefer running all agents in parallel; if the platform does not support parallel dispatch, run them sequentially respecting the dependency order from step 2.
 
+Keep parent-context pressure bounded:
+- If there are 1-4 unresolved items, direct parallel returns are fine
+- If there are 5+ unresolved items, launch in batches of at most 4 agents at a time
+- Require each resolver agent to return only a short status summary to the parent: todo handled, files changed, tests run or skipped, and any blocker that still needs follow-up
+
+If the todo set is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-todo-parallel/<run-id>/`:
+- Have each resolver write a compact artifact for its todo there
+- Return only a completion summary to the parent
+- Re-read only the artifacts that are needed to summarize outcomes, document learnings, or decide whether a todo is truly resolved
+
 ### 4. Commit & Resolve
 
 - Commit changes
@@ -44,6 +54,8 @@ GATE: STOP. Verify that the compound skill produced a solution document in `docs
 
 List all todos and identify those with `done` or `resolved` status, then delete them to keep the todo list clean and actionable.
 
+If a scratch directory was used and the user did not ask to inspect it, clean it up after todo cleanup succeeds.
+
 After cleanup, output a summary:
 
 ```
PATCH

echo "Gold patch applied."
