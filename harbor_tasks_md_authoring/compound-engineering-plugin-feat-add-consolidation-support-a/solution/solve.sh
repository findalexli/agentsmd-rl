#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "8. **Delete when the code is gone.** If the referenced code, controller, or work" "plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md" && grep -qF "In compact-safe mode, the overlap check is skipped (no Related Docs Finder subag" "plugins/compound-engineering/skills/ce-compound/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md b/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:compound-refresh
-description: Refresh stale or drifting learnings and pattern docs in docs/solutions/ by reviewing, updating, replacing, or archiving them against the current codebase. Use after refactors, migrations, dependency upgrades, or when a retrieved learning feels outdated or wrong. Also use when reviewing docs/solutions/ for accuracy, when a recently solved problem contradicts an existing learning, or when pattern docs no longer reflect current code.
-argument-hint: "[mode:autonomous] [optional: scope hint]"
+description: Refresh stale or drifting learnings and pattern docs in docs/solutions/ by reviewing, updating, consolidating, replacing, or deleting them against the current codebase. Use after refactors, migrations, dependency upgrades, or when a retrieved learning feels outdated or wrong. Also use when reviewing docs/solutions/ for accuracy, when a recently solved problem contradicts an existing learning, when pattern docs no longer reflect current code, or when multiple docs seem to cover the same topic and might benefit from consolidation.
+argument-hint: "[mode:autofix] [optional: scope hint]"
 disable-model-invocation: true
 ---
 
@@ -11,25 +11,25 @@ Maintain the quality of `docs/solutions/` over time. This workflow reviews exist
 
 ## Mode Detection
 
-Check if `$ARGUMENTS` contains `mode:autonomous`. If present, strip it from arguments (use the remainder as a scope hint) and run in **autonomous mode**.
+Check if `$ARGUMENTS` contains `mode:autofix`. If present, strip it from arguments (use the remainder as a scope hint) and run in **autofix mode**.
 
 | Mode | When | Behavior |
 |------|------|----------|
 | **Interactive** (default) | User is present and can answer questions | Ask for decisions on ambiguous cases, confirm actions |
-| **Autonomous** | `mode:autonomous` in arguments | No user interaction. Apply all unambiguous actions (Keep, Update, auto-Archive, Replace with sufficient evidence). Mark ambiguous cases as stale. Generate a summary report at the end. |
+| **Autofix** | `mode:autofix` in arguments | No user interaction. Apply all unambiguous actions (Keep, Update, Consolidate, auto-Delete, Replace with sufficient evidence). Mark ambiguous cases as stale. Generate a summary report at the end. |
 
-### Autonomous mode rules
+### Autofix mode rules
 
 - **Skip all user questions.** Never pause for input.
 - **Process all docs in scope.** No scope narrowing questions — if no scope hint was provided, process everything.
-- **Attempt all safe actions:** Keep (no-op), Update (fix references), auto-Archive (unambiguous criteria met), Replace (when evidence is sufficient). If a write succeeds, record it as **applied**. If a write fails (e.g., permission denied), record the action as **recommended** in the report and continue — do not stop or ask for permissions.
-- **Mark as stale when uncertain.** If classification is genuinely ambiguous (Update vs Replace vs Archive) or Replace evidence is insufficient, mark as stale with `status: stale`, `stale_reason`, and `stale_date` in the frontmatter. If even the stale-marking write fails, include it as a recommendation.
-- **Use conservative confidence.** In interactive mode, borderline cases get a user question. In autonomous mode, borderline cases get marked stale. Err toward stale-marking over incorrect action.
+- **Attempt all safe actions:** Keep (no-op), Update (fix references), Consolidate (merge and delete subsumed doc), auto-Delete (unambiguous criteria met), Replace (when evidence is sufficient). If a write succeeds, record it as **applied**. If a write fails (e.g., permission denied), record the action as **recommended** in the report and continue — do not stop or ask for permissions.
+- **Mark as stale when uncertain.** If classification is genuinely ambiguous (Update vs Replace vs Consolidate vs Delete) or Replace evidence is insufficient, mark as stale with `status: stale`, `stale_reason`, and `stale_date` in the frontmatter. If even the stale-marking write fails, include it as a recommendation.
+- **Use conservative confidence.** In interactive mode, borderline cases get a user question. In autofix mode, borderline cases get marked stale. Err toward stale-marking over incorrect action.
 - **Always generate a report.** The report is the primary deliverable. It has two sections: **Applied** (actions that were successfully written) and **Recommended** (actions that could not be written, with full rationale so a human can apply them or run the skill interactively). The report structure is the same regardless of what permissions were granted — the only difference is which section each action lands in.
 
 ## Interaction Principles
 
-**These principles apply to interactive mode only. In autonomous mode, skip all user questions and apply the autonomous mode rules above.**
+**These principles apply to interactive mode only. In autofix mode, skip all user questions and apply the autofix mode rules above.**
 
 Follow the same interaction style as `ce:brainstorm`:
 
@@ -46,7 +46,7 @@ The goal is not to force the user through a checklist. The goal is to help them
 Refresh in this order:
 
 1. Review the relevant individual learning docs first
-2. Note which learnings stayed valid, were updated, were replaced, or were archived
+2. Note which learnings stayed valid, were updated, were consolidated, were replaced, or were deleted
 3. Then review any pattern docs that depend on those learnings
 
 Why this order:
@@ -59,29 +59,32 @@ If the user starts by naming a pattern doc, you may begin there to understand th
 
 ## Maintenance Model
 
-For each candidate artifact, classify it into one of four outcomes:
+For each candidate artifact, classify it into one of five outcomes:
 
 | Outcome | Meaning | Default action |
 |---------|---------|----------------|
 | **Keep** | Still accurate and still useful | No file edit by default; report that it was reviewed and remains trustworthy |
 | **Update** | Core solution is still correct, but references drifted | Apply evidence-backed in-place edits |
-| **Replace** | The old artifact is now misleading, but there is a known better replacement | Create a trustworthy successor or revised pattern, then mark/archive the old artifact as needed |
-| **Archive** | No longer useful or applicable | Move the obsolete artifact to `docs/solutions/_archived/` with archive metadata when appropriate |
+| **Consolidate** | Two or more docs overlap heavily but are both correct | Merge unique content into the canonical doc, delete the subsumed doc |
+| **Replace** | The old artifact is now misleading, but there is a known better replacement | Create a trustworthy successor, then delete the old artifact |
+| **Delete** | No longer useful, applicable, or distinct | Delete the file — git history preserves it if anyone needs to recover it later |
 
 ## Core Rules
 
 1. **Evidence informs judgment.** The signals below are inputs, not a mechanical scorecard. Use engineering judgment to decide whether the artifact is still trustworthy.
 2. **Prefer no-write Keep.** Do not update a doc just to leave a review breadcrumb.
 3. **Match docs to reality, not the reverse.** When current code differs from a learning, update the learning to reflect the current code. The skill's job is doc accuracy, not code review — do not ask the user whether code changes were "intentional" or "a regression." If the code changed, the doc should match. If the user thinks the code is wrong, that is a separate concern outside this workflow.
-4. **Be decisive, minimize questions.** When evidence is clear (file renamed, class moved, reference broken), apply the update. In interactive mode, only ask the user when the right action is genuinely ambiguous. In autonomous mode, mark ambiguous cases as stale instead of asking. The goal is automated maintenance with human oversight on judgment calls, not a question for every finding.
+4. **Be decisive, minimize questions.** When evidence is clear (file renamed, class moved, reference broken), apply the update. In interactive mode, only ask the user when the right action is genuinely ambiguous. In autofix mode, mark ambiguous cases as stale instead of asking. The goal is automated maintenance with human oversight on judgment calls, not a question for every finding.
 5. **Avoid low-value churn.** Do not edit a doc just to fix a typo, polish wording, or make cosmetic changes that do not materially improve accuracy or usability.
 6. **Use Update only for meaningful, evidence-backed drift.** Paths, module names, related links, category metadata, code snippets, and clearly stale wording are fair game when fixing them materially improves accuracy.
 7. **Use Replace only when there is a real replacement.** That means either:
    - the current conversation contains a recently solved, verified replacement fix, or
    - the user has provided enough concrete replacement context to document the successor honestly, or
    - the codebase investigation found the current approach and can document it as the successor, or
    - newer docs, pattern docs, PRs, or issues provide strong successor evidence.
-8. **Archive when the code is gone.** If the referenced code, controller, or workflow no longer exists in the codebase and no successor can be found, recommend Archive — don't default to Keep just because the general advice is still "sound." A learning about a deleted feature misleads readers into thinking that feature still exists. When in doubt between Keep and Archive, ask the user (in interactive mode) or mark as stale (in autonomous mode). But missing referenced files with no matching code is **not** a doubt case — it is strong, unambiguous Archive evidence. Auto-archive it.
+8. **Delete when the code is gone.** If the referenced code, controller, or workflow no longer exists in the codebase and no successor can be found, delete the file — don't default to Keep just because the general advice is still "sound." A learning about a deleted feature misleads readers into thinking that feature still exists. When in doubt between Keep and Delete, ask the user (in interactive mode) or mark as stale (in autofix mode). But missing referenced files with no matching code is **not** a doubt case — it is strong, unambiguous Delete evidence. Auto-delete it.
+9. **Evaluate document-set design, not just accuracy.** In addition to checking whether each doc is accurate, evaluate whether it is still the right unit of knowledge. If two or more docs overlap heavily, determine whether they should remain separate, be cross-scoped more clearly, or be consolidated into one canonical document. Redundant docs are dangerous because they drift silently — two docs saying the same thing will eventually say different things.
+10. **Delete, don't archive.** There is no `_archived/` directory. When a doc is no longer useful, delete it. Git history preserves every deleted file — that is the archive. A dedicated archive directory creates problems: archived docs accumulate, pollute search results, and nobody reads them. If someone needs a deleted doc, `git log --diff-filter=D -- docs/solutions/` will find it.
 
 ## Scope Selection
 
@@ -90,9 +93,9 @@ Start by discovering learnings and pattern docs under `docs/solutions/`.
 Exclude:
 
 - `README.md`
-- `docs/solutions/_archived/`
+- `docs/solutions/_archived/` (legacy — if this directory exists, flag it for cleanup in the report)
 
-Find all `.md` files under `docs/solutions/`, excluding `README.md` files and anything under `_archived/`.
+Find all `.md` files under `docs/solutions/`, excluding `README.md` files and anything under `_archived/`. If an `_archived/` directory exists, note it in the report as a legacy artifact that should be cleaned up (files either restored or deleted).
 
 If `$ARGUMENTS` is provided, use it to narrow scope before proceeding. Try these matching strategies in order, stopping at the first that produces results:
 
@@ -101,7 +104,7 @@ If `$ARGUMENTS` is provided, use it to narrow scope before proceeding. Try these
 3. **Filename match** — match against filenames (partial matches are fine)
 4. **Content search** — search file contents for the argument as a keyword (useful for feature names or feature areas)
 
-If no matches are found, report that and ask the user to clarify. In autonomous mode, report the miss and stop — do not guess at scope.
+If no matches are found, report that and ask the user to clarify. In autofix mode, report the miss and stop — do not guess at scope.
 
 If no candidate docs are found, report:
 
@@ -133,7 +136,7 @@ When scope is broad (9+ candidate docs), do a lightweight triage before deep inv
 1. **Inventory** — read frontmatter of all candidate docs, group by module/component/category
 2. **Impact clustering** — identify areas with the densest clusters of learnings + pattern docs. A cluster of 5 learnings and 2 patterns covering the same module is higher-impact than 5 isolated single-doc areas, because staleness in one doc is likely to affect the others.
 3. **Spot-check drift** — for each cluster, check whether the primary referenced files still exist. Missing references in a high-impact cluster = strongest signal for where to start.
-4. **Recommend a starting area** — present the highest-impact cluster with a brief rationale and ask the user to confirm or redirect. In autonomous mode, skip the question and process all clusters in impact order.
+4. **Recommend a starting area** — present the highest-impact cluster with a brief rationale and ask the user to confirm or redirect. In autofix mode, skip the question and process all clusters in impact order.
 
 Example:
 
@@ -162,6 +165,7 @@ A learning has several dimensions that can independently go stale. Surface-level
 - **Code examples** — if the learning includes code snippets, do they still reflect the current implementation?
 - **Related docs** — are cross-referenced learnings and patterns still present and consistent?
 - **Auto memory** — does the auto memory directory contain notes in the same problem domain? Read MEMORY.md from the auto memory directory (the path is known from the system prompt context). If it does not exist or is empty, skip this dimension. A memory note describing a different approach than what the learning recommends is a supplementary drift signal.
+- **Overlap** — while investigating, note when another doc in scope covers the same problem domain, references the same files, or recommends a similar solution. For each overlap, record: the two file paths, which dimensions overlap (problem, solution, root cause, files, prevention), and which doc appears broader or more current. These signals feed Phase 1.75 (Document-Set Analysis).
 
 Match investigation depth to the learning's specificity — a learning referencing exact file paths and code snippets needs more verification than one describing a general principle.
 
@@ -174,20 +178,20 @@ The critical distinction is whether the drift is **cosmetic** (references moved
 
 **The boundary:** if you find yourself rewriting the solution section or changing what the learning recommends, stop — that is Replace, not Update.
 
-**Memory-sourced drift signals** are supplementary, not primary. A memory note describing a different approach does not alone justify Replace or Archive. Use memory signals to:
+**Memory-sourced drift signals** are supplementary, not primary. A memory note describing a different approach does not alone justify Replace or Delete. Use memory signals to:
 - Corroborate codebase-sourced drift (strengthens the case for Replace)
 - Prompt deeper investigation when codebase evidence is borderline
 - Add context to the evidence report ("(auto memory [claude]) notes suggest approach X may have changed since this learning was written")
 
-In autonomous mode, memory-only drift (no codebase corroboration) should result in stale-marking, not action.
+In autofix mode, memory-only drift (no codebase corroboration) should result in stale-marking, not action.
 
 ### Judgment Guidelines
 
 Three guidelines that are easy to get wrong:
 
 1. **Contradiction = strong Replace signal.** If the learning's recommendation conflicts with current code patterns or a recently verified fix, that is not a minor drift — the learning is actively misleading. Classify as Replace.
 2. **Age alone is not a stale signal.** A 2-year-old learning that still matches current code is fine. Only use age as a prompt to inspect more carefully.
-3. **Check for successors before archiving.** Before recommending Replace or Archive, look for newer learnings, pattern docs, PRs, or issues covering the same problem space. If successor evidence exists, prefer Replace over Archive so readers are directed to the newer guidance.
+3. **Check for successors before deleting.** Before recommending Replace or Delete, look for newer learnings, pattern docs, PRs, or issues covering the same problem space. If successor evidence exists, prefer Replace over Delete so readers are directed to the newer guidance.
 
 ## Phase 1.5: Investigate Pattern Docs
 
@@ -197,6 +201,65 @@ Pattern docs are high-leverage — a stale pattern is more dangerous than a stal
 
 A pattern doc with no clear supporting learnings is a stale signal — investigate carefully before keeping it unchanged.
 
+## Phase 1.75: Document-Set Analysis
+
+After investigating individual docs, step back and evaluate the document set as a whole. The goal is to catch problems that only become visible when comparing docs to each other — not just to reality.
+
+### Overlap Detection
+
+For docs that share the same module, component, tags, or problem domain, compare them across these dimensions:
+
+- **Problem statement** — do they describe the same underlying problem?
+- **Solution shape** — do they recommend the same approach, even if worded differently?
+- **Referenced files** — do they point to the same code paths?
+- **Prevention rules** — do they repeat the same prevention bullets?
+- **Root cause** — do they identify the same root cause?
+
+High overlap across 3+ dimensions is a strong Consolidate signal. The question to ask: "Would a future maintainer need to read both docs to get the current truth, or is one mostly repeating the other?"
+
+### Supersession Signals
+
+Detect "older narrow precursor, newer canonical doc" patterns:
+
+- A newer doc covers the same files, same workflow, and broader runtime behavior than an older doc
+- An older doc describes a specific incident that a newer doc generalizes into a pattern
+- Two docs recommend the same fix but the newer one has better context, examples, or scope
+
+When a newer doc clearly subsumes an older one, the older doc is a consolidation candidate — its unique content (if any) should be merged into the newer doc, and the older doc should be deleted.
+
+### Canonical Doc Identification
+
+For each topic cluster (docs sharing a problem domain), identify which doc is the **canonical source of truth**:
+
+- Usually the most recent, broadest, most accurate doc in the cluster
+- The one a maintainer should find first when searching for this topic
+- The one that other docs should point to, not duplicate
+
+All other docs in the cluster are either:
+- **Distinct** — they cover a meaningfully different sub-problem and have independent retrieval value. Keep them separate.
+- **Subsumed** — their unique content fits as a section in the canonical doc. Consolidate.
+- **Redundant** — they add nothing the canonical doc doesn't already say. Delete.
+
+### Retrieval-Value Test
+
+Before recommending that two docs stay separate, apply this test: "If a maintainer searched for this topic six months from now, would having these as separate docs improve discoverability, or just create drift risk?"
+
+Separate docs earn their keep only when:
+- They cover genuinely different sub-problems that someone might search for independently
+- They target different audiences or contexts (e.g., one is about debugging, another about prevention)
+- Merging them would create an unwieldy doc that is harder to navigate than two focused ones
+
+If none of these apply, prefer consolidation. Two docs covering the same ground will eventually drift apart and contradict each other — that is worse than a slightly longer single doc.
+
+### Cross-Doc Conflict Check
+
+Look for outright contradictions between docs in scope:
+- Doc A says "always use approach X" while Doc B says "avoid approach X"
+- Doc A references a file path that Doc B says was deprecated
+- Doc A and Doc B describe different root causes for what appears to be the same problem
+
+Contradictions between docs are more urgent than individual staleness — they actively confuse readers. Flag these for immediate resolution, either through Consolidate (if one is right and the other is a stale version of the same truth) or through targeted Update/Replace.
+
 ## Subagent Strategy
 
 Use subagents for context isolation when investigating multiple artifacts — not just because the task sounds complex. Choose the lightest approach that fits:
@@ -216,10 +279,10 @@ Use subagents for context isolation when investigating multiple artifacts — no
 
 There are two subagent roles:
 
-1. **Investigation subagents** — read-only. They must not edit files, create successors, or archive anything. Each returns: file path, evidence, recommended action, confidence, and open questions. These can run in parallel when artifacts are independent.
-2. **Replacement subagents** — write a single new learning to replace a stale one. These run **one at a time, sequentially** (each replacement subagent may need to read significant code, and running multiple in parallel risks context exhaustion). The orchestrator handles all archival and metadata updates after each replacement completes.
+1. **Investigation subagents** — read-only. They must not edit files, create successors, or delete anything. Each returns: file path, evidence, recommended action, confidence, and open questions. These can run in parallel when artifacts are independent.
+2. **Replacement subagents** — write a single new learning to replace a stale one. These run **one at a time, sequentially** (each replacement subagent may need to read significant code, and running multiple in parallel risks context exhaustion). The orchestrator handles all deletions and metadata updates after each replacement completes.
 
-The orchestrator merges investigation results, detects contradictions, coordinates replacement subagents, and performs all archival/metadata edits centrally. In interactive mode, it asks the user questions on ambiguous cases. In autonomous mode, it marks ambiguous cases as stale instead. If two artifacts overlap or discuss the same root issue, investigate them together rather than parallelizing.
+The orchestrator merges investigation results, detects contradictions, coordinates replacement subagents, and performs all deletions/metadata edits centrally. In interactive mode, it asks the user questions on ambiguous cases. In autofix mode, it marks ambiguous cases as stale instead. If two artifacts overlap or discuss the same root issue, investigate them together rather than parallelizing.
 
 ## Phase 2: Classify the Right Maintenance Action
 
@@ -233,6 +296,26 @@ The learning is still accurate and useful. Do not edit the file — report that
 
 The core solution is still valid but references have drifted (paths, class names, links, code snippets, metadata). Apply the fixes directly.
 
+### Consolidate
+
+Choose **Consolidate** when Phase 1.75 identified docs that overlap heavily but are both materially correct. This is different from Update (which fixes drift in a single doc) and Replace (which rewrites misleading guidance). Consolidate handles the "both right, one subsumes the other" case.
+
+**When to consolidate:**
+
+- Two docs describe the same problem and recommend the same (or compatible) solution
+- One doc is a narrow precursor and a newer doc covers the same ground more broadly
+- The unique content from the subsumed doc can fit as a section or addendum in the canonical doc
+- Keeping both creates drift risk without meaningful retrieval benefit
+
+**When NOT to consolidate** (apply the Retrieval-Value Test from Phase 1.75):
+
+- The docs cover genuinely different sub-problems that someone would search for independently
+- Merging would create an unwieldy doc that harms navigation more than drift risk harms accuracy
+
+**Consolidate vs Delete:** If the subsumed doc has unique content worth preserving (edge cases, alternative approaches, extra prevention rules), use Consolidate to merge that content first. If the subsumed doc adds nothing the canonical doc doesn't already say, skip straight to Delete.
+
+The Consolidate action is: merge unique content from the subsumed doc into the canonical doc, then delete the subsumed doc. Not archive — delete. Git history preserves it.
+
 ### Replace
 
 Choose **Replace** when the learning's core guidance is now misleading — the recommended fix changed materially, the root cause or architecture shifted, or the preferred pattern is different.
@@ -249,71 +332,64 @@ By the time you identify a Replace candidate, Phase 1 investigation has already
    - Report what evidence you found and what is missing
    - Recommend the user run `ce:compound` after their next encounter with that area, when they have fresh problem-solving context
 
-### Archive
+### Delete
 
-Choose **Archive** when:
+Choose **Delete** when:
 
-- The code or workflow no longer exists
+- The code or workflow no longer exists and the problem domain is gone
 - The learning is obsolete and has no modern replacement worth documenting
-- The learning is redundant and no longer useful on its own
+- The learning is fully redundant with another doc (use Consolidate if there is unique content to merge first)
 - There is no meaningful successor evidence suggesting it should be replaced instead
 
-Action:
-
-- Move the file to `docs/solutions/_archived/`, preserving directory structure when helpful
-- Add:
-  - `archived_date: YYYY-MM-DD`
-  - `archive_reason: [why it was archived]`
+Action: delete the file. No archival directory, no metadata — just delete it. Git history preserves every deleted file if recovery is ever needed.
 
-### Before archiving: check if the problem domain is still active
+### Before deleting: check if the problem domain is still active
 
-When a learning's referenced files are gone, that is strong evidence — but only that the **implementation** is gone. Before archiving, reason about whether the **problem the learning solves** is still a concern in the codebase:
+When a learning's referenced files are gone, that is strong evidence — but only that the **implementation** is gone. Before deleting, reason about whether the **problem the learning solves** is still a concern in the codebase:
 
-- A learning about session token storage where `auth_token.rb` is gone — does the application still handle session tokens? If so, the concept persists under a new implementation. That is Replace, not Archive.
-- A learning about a deprecated API endpoint where the entire feature was removed — the problem domain is gone. That is Archive.
+- A learning about session token storage where `auth_token.rb` is gone — does the application still handle session tokens? If so, the concept persists under a new implementation. That is Replace, not Delete.
+- A learning about a deprecated API endpoint where the entire feature was removed — the problem domain is gone. That is Delete.
 
 Do not search mechanically for keywords from the old learning. Instead, understand what problem the learning addresses, then investigate whether that problem domain still exists in the codebase. The agent understands concepts — use that understanding to look for where the problem lives now, not where the old code used to be.
 
-**Auto-archive only when both the implementation AND the problem domain are gone:**
+**Auto-delete only when both the implementation AND the problem domain are gone:**
 
 - the referenced code is gone AND the application no longer deals with that problem domain
-- the learning is fully superseded by a clearly better successor
-- the document is plainly redundant and adds no distinct value
+- the learning is fully superseded by a clearly better successor AND the old doc adds no distinct value
+- the document is plainly redundant and adds nothing the canonical doc doesn't already say
 
 If the implementation is gone but the problem domain persists (the app still does auth, still processes payments, still handles migrations), classify as **Replace** — the problem still matters and the current approach should be documented.
 
-Do not keep a learning just because its general advice is "still sound" — if the specific code it references is gone, the learning misleads readers. But do not archive a learning whose problem domain is still active — that knowledge gap should be filled with a replacement.
-
-If there is a clearly better successor, strongly consider **Replace** before **Archive** so the old artifact points readers toward the newer guidance.
+Do not keep a learning just because its general advice is "still sound" — if the specific code it references is gone, the learning misleads readers. But do not delete a learning whose problem domain is still active — that knowledge gap should be filled with a replacement.
 
 ## Pattern Guidance
 
-Apply the same four outcomes (Keep, Update, Replace, Archive) to pattern docs, but evaluate them as **derived guidance** rather than incident-level learnings. Key differences:
+Apply the same five outcomes (Keep, Update, Consolidate, Replace, Delete) to pattern docs, but evaluate them as **derived guidance** rather than incident-level learnings. Key differences:
 
 - **Keep**: the underlying learnings still support the generalized rule and examples remain representative
 - **Update**: the rule holds but examples, links, scope, or supporting references drifted
+- **Consolidate**: two pattern docs generalize the same set of learnings or cover the same design concern — merge into one canonical pattern
 - **Replace**: the generalized rule is now misleading, or the underlying learnings support a different synthesis. Base the replacement on the refreshed learning set — do not invent new rules from guesswork
-- **Archive**: the pattern is no longer valid, no longer recurring, or fully subsumed by a stronger pattern doc
-
-If "archive" feels too strong but the pattern should no longer be elevated, reduce its prominence in place if the docs structure supports that.
+- **Delete**: the pattern is no longer valid, no longer recurring, or fully subsumed by a stronger pattern doc with no unique content remaining
 
 ## Phase 3: Ask for Decisions
 
-### Autonomous mode
+### Autofix mode
 
 **Skip this entire phase. Do not ask any questions. Do not present options. Do not wait for input.** Proceed directly to Phase 4 and execute all actions based on the classifications from Phase 2:
 
-- Unambiguous Keep, Update, auto-Archive, and Replace (with sufficient evidence) → execute directly
+- Unambiguous Keep, Update, Consolidate, auto-Delete, and Replace (with sufficient evidence) → execute directly
 - Ambiguous cases → mark as stale
 - Then generate the report (see Output Format)
 
 ### Interactive mode
 
-Most Updates should be applied directly without asking. Only ask the user when:
+Most Updates and Consolidations should be applied directly without asking. Only ask the user when:
 
-- The right action is genuinely ambiguous (Update vs Replace vs Archive)
-- You are about to Archive a document **and** the evidence is not unambiguous (see auto-archive criteria in Phase 2). When auto-archive criteria are met, proceed without asking.
-- You are about to create a successor via `ce:compound`
+- The right action is genuinely ambiguous (Update vs Replace vs Consolidate vs Delete)
+- You are about to Delete a document **and** the evidence is not unambiguous (see auto-delete criteria in Phase 2). When auto-delete criteria are met, proceed without asking.
+- You are about to Consolidate and the choice of canonical doc is not clear-cut
+- You are about to create a successor via Replace
 
 Do **not** ask questions about whether code changes were intentional, whether the user wants to fix bugs in the code, or other concerns outside doc maintenance. Stay in your lane — doc accuracy.
 
@@ -340,7 +416,7 @@ For a single artifact, present:
 Then ask:
 
 ```text
-This [learning/pattern] looks like a [Update/Keep/Replace/Archive].
+This [learning/pattern] looks like a [Keep/Update/Consolidate/Replace/Delete].
 
 Why: [one-sentence rationale based on the evidence]
 
@@ -351,22 +427,24 @@ What would you like to do?
 3. Skip for now
 ```
 
-Do not list all four actions unless all four are genuinely plausible.
+Do not list all five actions unless all five are genuinely plausible.
 
 #### Batch Scope
 
 For several learnings:
 
 1. Group obvious **Keep** cases together
 2. Group obvious **Update** cases together when the fixes are straightforward
-3. Present **Replace** cases individually or in very small groups
-4. Present **Archive** cases individually unless they are strong auto-archive candidates
+3. Present **Consolidate** cases together when the canonical doc is clear
+4. Present **Replace** cases individually or in very small groups
+5. Present **Delete** cases individually unless they are strong auto-delete candidates
 
 Ask for confirmation in stages:
 
 1. Confirm grouped Keep/Update recommendations
-2. Then handle Replace one at a time
-3. Then handle Archive one at a time unless the archive is unambiguous and safe to auto-apply
+2. Then handle Consolidate groups (present the canonical doc and what gets merged)
+3. Then handle Replace one at a time
+4. Then handle Delete one at a time unless the deletion is unambiguous and safe to auto-apply
 
 #### Broad Scope
 
@@ -407,6 +485,20 @@ Examples that should **not** be in-place updates:
 
 Those cases require **Replace**, not Update.
 
+### Consolidate Flow
+
+The orchestrator handles consolidation directly (no subagent needed — the docs are already read and the merge is a focused edit). Process Consolidate candidates by topic cluster. For each cluster identified in Phase 1.75:
+
+1. **Confirm the canonical doc** — the broader, more current, more accurate doc in the cluster.
+2. **Extract unique content** from the subsumed doc(s) — anything the canonical doc does not already cover. This might be specific edge cases, additional prevention rules, or alternative debugging approaches.
+3. **Merge unique content** into the canonical doc in a natural location. Do not just append — integrate it where it logically belongs. If the unique content is small (a bullet point, a sentence), inline it. If it is a substantial sub-topic, add it as a clearly labeled section.
+4. **Update cross-references** — if any other docs reference the subsumed doc, update those references to point to the canonical doc.
+5. **Delete the subsumed doc.** Do not archive it, do not add redirect metadata — just delete the file. Git history preserves it.
+
+If a doc cluster has 3+ overlapping docs, process pairwise: consolidate the two most overlapping docs first, then evaluate whether the merged result should be consolidated with the next doc.
+
+**Structural edits beyond merge:** Consolidate also covers the reverse case. If one doc has grown unwieldy and covers multiple distinct problems that would benefit from separate retrieval, it is valid to recommend splitting it. Only do this when the sub-topics are genuinely independent and a maintainer might search for one without needing the other.
+
 ### Replace Flow
 
 Process Replace candidates **one at a time, sequentially**. Each replacement is written by a subagent to protect the main context window.
@@ -418,9 +510,7 @@ Process Replace candidates **one at a time, sequentially**. Each replacement is
    - A summary of the investigation evidence (what changed, what the current code does, why the old guidance is misleading)
    - The target path and category (same category as the old learning unless the category itself changed)
 2. The subagent writes the new learning following `ce:compound`'s document format: YAML frontmatter (title, category, date, module, component, tags), problem description, root cause, current solution with code examples, and prevention tips. It should use dedicated file search and read tools if it needs additional context beyond what was passed.
-3. After the subagent completes, the orchestrator:
-   - Adds `superseded_by: [new learning path]` to the old learning's frontmatter
-   - Moves the old learning to `docs/solutions/_archived/`
+3. After the subagent completes, the orchestrator deletes the old learning file. The new learning's frontmatter may include `supersedes: [old learning filename]` for traceability, but this is optional — the git history and commit message provide the same information.
 
 **When evidence is insufficient:**
 
@@ -429,9 +519,9 @@ Process Replace candidates **one at a time, sequentially**. Each replacement is
 2. Report what evidence was found and what is missing
 3. Recommend the user run `ce:compound` after their next encounter with that area
 
-### Archive Flow
+### Delete Flow
 
-Archive only when a learning is clearly obsolete or redundant. Do not archive a document just because it is old.
+Delete only when a learning is clearly obsolete, redundant (with no unique content to merge), or its problem domain is gone. Do not delete a document just because it is old — age alone is not a signal.
 
 ## Output Format
 
@@ -446,30 +536,33 @@ Scanned: N learnings
 
 Kept: X
 Updated: Y
+Consolidated: C
 Replaced: Z
-Archived: W
+Deleted: W
 Skipped: V
 Marked stale: S
 ```
 
 Then for EVERY file processed, list:
 - The file path
-- The classification (Keep/Update/Replace/Archive/Stale)
+- The classification (Keep/Update/Consolidate/Replace/Delete/Stale)
 - What evidence was found -- tag any memory-sourced findings with "(auto memory [claude])" to distinguish them from codebase-sourced evidence
 - What action was taken (or recommended)
+- For Consolidate: which doc was canonical, what unique content was merged, what was deleted
 
 For **Keep** outcomes, list them under a reviewed-without-edits section so the result is visible without creating git churn.
 
-### Autonomous mode output
+### Autofix mode report
 
-In autonomous mode, the report is the sole deliverable — there is no user present to ask follow-up questions, so the report must be self-contained and complete. **Print the full report. Do not abbreviate, summarize, or skip sections.**
+In autofix mode, the report is the sole deliverable — there is no user present to ask follow-up questions, so the report must be self-contained and complete. **Print the full report. Do not abbreviate, summarize, or skip sections.**
 
 Split actions into two sections:
 
 **Applied** (writes that succeeded):
 - For each **Updated** file: the file path, what references were fixed, and why
+- For each **Consolidated** cluster: the canonical doc, what unique content was merged from each subsumed doc, and the subsumed docs that were deleted
 - For each **Replaced** file: what the old learning recommended vs what the current code does, and the path to the new successor
-- For each **Archived** file: the file path and what referenced code/workflow is gone
+- For each **Deleted** file: the file path and why it was removed (problem domain gone, fully redundant, etc.)
 - For each **Marked stale** file: the file path, what evidence was found, and why it was ambiguous
 
 **Recommended** (actions that could not be written — e.g., permission denied):
@@ -478,6 +571,9 @@ Split actions into two sections:
 
 If all writes succeed, the Recommended section is empty. If no writes succeed (e.g., read-only invocation), all actions appear under Recommended — the report becomes a maintenance plan.
 
+**Legacy cleanup** (if `docs/solutions/_archived/` exists):
+- List archived files found and recommend disposition: restore (if still relevant), delete (if truly obsolete), or consolidate (if overlapping with active docs)
+
 ## Phase 5: Commit Changes
 
 After all actions are executed and the report is generated, handle committing the changes. Skip this phase if no files were modified (all Keep, or all writes failed).
@@ -489,7 +585,7 @@ Before offering options, check:
 2. Whether the working tree has other uncommitted changes beyond what compound-refresh modified
 3. Recent commit messages to match the repo's commit style
 
-### Autonomous mode
+### Autofix mode
 
 Use sensible defaults — no user to ask:
 
@@ -525,13 +621,15 @@ First, run `git branch --show-current` to determine the current branch. Then pre
 ### Commit message
 
 Write a descriptive commit message that:
-- Summarizes what was refreshed (e.g., "update 3 stale learnings, archive 1 obsolete doc")
+- Summarizes what was refreshed (e.g., "update 3 stale learnings, consolidate 2 overlapping docs, delete 1 obsolete doc")
 - Follows the repo's existing commit conventions (check recent git log for style)
 - Is succinct — the details are in the changed files themselves
 
 ## Relationship to ce:compound
 
 - `ce:compound` captures a newly solved, verified problem
-- `ce:compound-refresh` maintains older learnings as the codebase evolves
+- `ce:compound-refresh` maintains older learnings as the codebase evolves — both their individual accuracy and their collective design as a document set
 
 Use **Replace** only when the refresh process has enough real evidence to write a trustworthy successor. When evidence is insufficient, mark as stale and recommend `ce:compound` for when the user next encounters that problem area.
+
+Use **Consolidate** proactively when the document set has grown organically and redundancy has crept in. Every `ce:compound` invocation adds a new doc — over time, multiple docs may cover the same problem from slightly different angles. Periodic consolidation keeps the document set lean and authoritative.
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -122,7 +122,11 @@ Launch these subagents IN PARALLEL. Each returns text data to the orchestrator.
    - Identifies cross-references and links
    - Finds related GitHub issues
    - Flags any related learning or pattern docs that may now be stale, contradicted, or overly broad
-   - Returns: Links, relationships, and any refresh candidates
+   - **Assesses overlap** with the new doc being created across five dimensions: problem statement, root cause, solution approach, referenced files, and prevention rules. Score as:
+     - **High**: 4-5 dimensions match — essentially the same problem solved again
+     - **Moderate**: 2-3 dimensions match — same area but different angle or solution
+     - **Low**: 0-1 dimensions match — related but distinct
+   - Returns: Links, relationships, refresh candidates, and overlap assessment (score + which dimensions matched)
 
    **Search strategy (grep-first filtering for efficiency):**
 
@@ -153,10 +157,22 @@ Launch these subagents IN PARALLEL. Each returns text data to the orchestrator.
 The orchestrating agent (main conversation) performs these steps:
 
 1. Collect all text results from Phase 1 subagents
-2. Assemble complete markdown file from the collected pieces
-3. Validate YAML frontmatter against schema
-4. Create directory if needed: `mkdir -p docs/solutions/[category]/`
-5. Write the SINGLE final file: `docs/solutions/[category]/[filename].md`
+2. **Check the overlap assessment** from the Related Docs Finder before deciding what to write:
+
+   | Overlap | Action |
+   |---------|--------|
+   | **High** — existing doc covers the same problem, root cause, and solution | **Update the existing doc** with fresher context (new code examples, updated references, additional prevention tips) rather than creating a duplicate. The existing doc's path and structure stay the same. |
+   | **Moderate** — same problem area but different angle, root cause, or solution | **Create the new doc** normally. Flag the overlap for Phase 2.5 to recommend consolidation review. |
+   | **Low or none** | **Create the new doc** normally. |
+
+   The reason to update rather than create: two docs describing the same problem and solution will inevitably drift apart. The newer context is fresher and more trustworthy, so fold it into the existing doc rather than creating a second one that immediately needs consolidation.
+
+   When updating an existing doc, preserve its file path and frontmatter structure. Update the solution, code examples, prevention tips, and any stale references. Add a `last_updated: YYYY-MM-DD` field to the frontmatter. Do not change the title unless the problem framing has materially shifted.
+
+3. Assemble complete markdown file from the collected pieces
+4. Validate YAML frontmatter against schema
+5. Create directory if needed: `mkdir -p docs/solutions/[category]/`
+6. Write the file: either the updated existing doc or the new `docs/solutions/[category]/[filename].md`
 
 </sequential_tasks>
 
@@ -173,6 +189,7 @@ It makes sense to invoke `ce:compound-refresh` when one or more of these are tru
 3. The current work involved a refactor, migration, rename, or dependency upgrade that likely invalidated references in older docs
 4. A pattern doc now looks overly broad, outdated, or no longer supported by the refreshed reality
 5. The Related Docs Finder surfaced high-confidence refresh candidates in the same problem space
+6. The Related Docs Finder reported **moderate overlap** with an existing doc — there may be consolidation opportunities that benefit from a focused review
 
 It does **not** make sense to invoke `ce:compound-refresh` when:
 
@@ -259,7 +276,7 @@ re-run /compound in a fresh session.
 
 **No subagents are launched. No parallel tasks. One file written.**
 
-In compact-safe mode, only suggest `ce:compound-refresh` if there is an obvious narrow refresh target. Do not broaden into a large refresh sweep from a compact-safe session.
+In compact-safe mode, the overlap check is skipped (no Related Docs Finder subagent). This means compact-safe mode may create a doc that overlaps with an existing one. That is acceptable — `ce:compound-refresh` will catch it later. Only suggest `ce:compound-refresh` if there is an obvious narrow refresh target. Do not broaden into a large refresh sweep from a compact-safe session.
 
 ---
 
@@ -310,7 +327,8 @@ In compact-safe mode, only suggest `ce:compound-refresh` if there is an obvious
 |----------|-----------|
 | Subagents write files like `context-analysis.md`, `solution-draft.md` | Subagents return text data; orchestrator writes one final file |
 | Research and assembly run in parallel | Research completes → then assembly runs |
-| Multiple files created during workflow | Single file: `docs/solutions/[category]/[filename].md` |
+| Multiple files created during workflow | One file written or updated: `docs/solutions/[category]/[filename].md` |
+| Creating a new doc when an existing doc covers the same problem | Check overlap assessment; update the existing doc when overlap is high |
 
 ## Success Output
 
@@ -344,6 +362,19 @@ What's next?
 5. Other
 ```
 
+**Alternate output (when updating an existing doc due to high overlap):**
+
+```
+✓ Documentation updated (existing doc refreshed with current context)
+
+Overlap detected: docs/solutions/performance-issues/n-plus-one-queries.md
+  Matched dimensions: problem statement, root cause, solution, referenced files
+  Action: Updated existing doc with fresher code examples and prevention tips
+
+File updated:
+- docs/solutions/performance-issues/n-plus-one-queries.md (added last_updated: 2026-03-24)
+```
+
 ## The Compounding Philosophy
 
 This creates a compounding knowledge system:
PATCH

echo "Gold patch applied."
