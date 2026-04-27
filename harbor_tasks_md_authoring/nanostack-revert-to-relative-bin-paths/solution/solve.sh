#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "**Saving artifacts is not optional.** Every skill must save its artifact after c" "SKILL.md" && grep -qF "bin/save-artifact.sh compound '<json with phase, summary including solutions_cre" "compound/SKILL.md" && grep -qF "bin/save-artifact.sh plan '<json with phase, summary including planned_files arr" "plan/SKILL.md" && grep -qF "bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihoo" "qa/SKILL.md" && grep -qF "bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findi" "review/SKILL.md" && grep -qF "bin/save-artifact.sh security '<json with phase, mode, summary, findings, confli" "security/SKILL.md" && grep -qF "bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url" "ship/SKILL.md" && grep -qF "bin/save-artifact.sh think '<json with phase, summary including value_propositio" "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -57,21 +57,10 @@ Skills `/review`, `/security`, and `/qa` support intensity modes:
 
 Skills auto-suggest a mode based on the diff, but the user always decides.
 
-## Script Resolution
-
-All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are relative to the nanostack skill root, not to the user's project directory.
-
-**When you need to run a bin/ script, prefix it with `~/.claude/skills/nanostack/`:**
-
-```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh think '{"phase":"think",...}'
-~/.claude/skills/nanostack/bin/find-artifact.sh plan 2
-```
-
-This works for all standard installations (git clone and npx). Saving artifacts is not optional — every skill must save its artifact after completing.
-
 ## Artifact Persistence
 
+**Saving artifacts is not optional.** Every skill must save its artifact after completing.
+
 Skills automatically save their output to `.nanostack/` after every run:
 
 ```bash
diff --git a/compound/SKILL.md b/compound/SKILL.md
@@ -25,12 +25,12 @@ After a sprint or a significant fix, extract what you learned into structured, s
 Find what happened during this sprint:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh think 2
-~/.claude/skills/nanostack/bin/find-artifact.sh plan 2
-~/.claude/skills/nanostack/bin/find-artifact.sh review 2
-~/.claude/skills/nanostack/bin/find-artifact.sh qa 2
-~/.claude/skills/nanostack/bin/find-artifact.sh security 2
-~/.claude/skills/nanostack/bin/find-artifact.sh ship 2
+bin/find-artifact.sh think 2
+bin/find-artifact.sh plan 2
+bin/find-artifact.sh review 2
+bin/find-artifact.sh qa 2
+bin/find-artifact.sh security 2
+bin/find-artifact.sh ship 2
 ```
 
 Not all artifacts will exist. Read what's available. Focus on:
@@ -56,9 +56,9 @@ Skip:
 Before creating a new document, search for related ones:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-solution.sh "relevant keywords"
-~/.claude/skills/nanostack/bin/find-solution.sh --tag relevant-tag
-~/.claude/skills/nanostack/bin/find-solution.sh --file affected/file/path
+bin/find-solution.sh "relevant keywords"
+bin/find-solution.sh --tag relevant-tag
+bin/find-solution.sh --file affected/file/path
 ```
 
 If a closely related solution exists:
@@ -72,7 +72,7 @@ Do not create duplicates. One good document beats two partial ones.
 For each significant learning, create a document:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-solution.sh <type> "<title>" "tag1,tag2,tag3"
+bin/save-solution.sh <type> "<title>" "tag1,tag2,tag3"
 ```
 
 Types:
@@ -127,7 +127,7 @@ Total solutions in project: 12
 ## Save Artifact
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. Summarize how many solutions were created/updated and their types.
@@ -143,5 +143,5 @@ The `context_checkpoint` is mandatory. Summarize how many solutions were created
 - **Use the exact file paths.** `src/api/webhooks/stripe.ts` is searchable. "The webhook file" is not.
 - **Tags are for search, not decoration.** Use terms someone would grep for: `stripe`, `webhooks`, `hmac`, not `payment-processing-integration`.
 - **Set severity accurately.** Solutions are ranked by severity when searched. Don't leave everything as medium.
-- **Update, don't duplicate.** If ~/.claude/skills/nanostack/bin/find-solution.sh returns a close match, update that document.
+- **Update, don't duplicate.** If bin/find-solution.sh returns a close match, update that document.
 - **The Prevention section is the highest-value section.** A bug fix helps once. A prevention rule helps every future sprint.
diff --git a/plan/SKILL.md b/plan/SKILL.md
@@ -17,7 +17,7 @@ You turn validated ideas into executable steps. Every file gets named. Every ste
 
 - **Read the /think artifact** if one exists for this project:
   ```bash
-  ~/.claude/skills/nanostack/bin/find-artifact.sh think 2
+  bin/find-artifact.sh think 2
   ```
   If found, extract and use:
   - `key_risk` → add to your Risks section. This was already validated by /think.
@@ -131,7 +131,7 @@ Present the plan to the user. Wait for explicit approval before executing. If th
 Always persist the plan after presenting it to the user:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. Summarize the plan scope, list planned files, and document key decisions (e.g., "small scope, 2 files" or "chose X over Y because Z").
diff --git a/qa/SKILL.md b/qa/SKILL.md
@@ -78,7 +78,7 @@ After functional tests pass, take screenshots of every key state and analyze the
 **Read the plan artifact first:**
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh plan 2
+bin/find-artifact.sh plan 2
 ```
 
 If the plan specifies product standards (shadcn/ui, Tailwind, dark mode, specific component library), use those as your checklist. Don't guess what the UI should look like. The plan defines the spec. If the plan said "shadcn/ui + Tailwind" and the output uses raw CSS, that's a finding.
@@ -196,7 +196,7 @@ Report progress as you go. After each test group (happy path, error states, edge
 Always persist the QA results after completing the run:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. Summarize tests passed/failed, bugs found/fixed, and WTF likelihood.
diff --git a/review/SKILL.md b/review/SKILL.md
@@ -39,14 +39,14 @@ Calibrate depth by diff size: **Small** (< 100 lines, quick pass) / **Medium** (
 Find the plan artifact and extract context for the review:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh plan 2
+bin/find-artifact.sh plan 2
 ```
 
 Search for past solutions related to the files being changed:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-solution.sh --file <changed-file-path>
-~/.claude/skills/nanostack/bin/find-solution.sh "<relevant-keywords>"
+bin/find-solution.sh --file <changed-file-path>
+bin/find-solution.sh "<relevant-keywords>"
 ```
 
 The output shows ranked summaries. Read the summaries first, then load only the solutions relevant to the current review. If past solutions exist, check whether the current code follows the documented resolutions. If it contradicts a past solution, flag it.
@@ -63,7 +63,7 @@ Always run if a recent plan artifact exists. In `--quick` mode, drift is informa
 Run the scope drift script:
 
 ```bash
-~/.claude/skills/nanostack/bin/scope-drift.sh
+bin/scope-drift.sh
 ```
 
 The script returns JSON with `status` (clean / drift_detected / requirements_missing), `out_of_scope_files`, and `missing_files`. Config/lock files are automatically exempt.
@@ -113,7 +113,7 @@ Then group by severity: **Blocking** (must fix), **Should Fix** (tech debt, conf
 After completing both passes, check for conflicts with prior `/security` findings:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh security 30
+bin/find-artifact.sh security 30
 ```
 
 If an artifact is found, cross-reference your findings against it. Read `reference/conflict-precedents.md` for known conflict patterns and resolutions.
@@ -133,7 +133,7 @@ When a conflict is detected, mark it inline:
 Always persist the review after completing it:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. Summarize findings count and severity, scope drift status, and any auto-fixes applied.
diff --git a/security/SKILL.md b/security/SKILL.md
@@ -34,7 +34,7 @@ Auto-suggest:
 **Read the plan artifact** if one exists:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh plan 2
+bin/find-artifact.sh plan 2
 ```
 
 If found:
@@ -206,7 +206,7 @@ Always close with **What's solid**: 2-3 specific things the codebase does well o
 Always check for conflicts with prior `/review` findings if a review artifact exists:
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh review 30
+bin/find-artifact.sh review 30
 ```
 
 Read `reference/conflict-precedents.md` for known conflict patterns. When detected, mark inline:
@@ -224,7 +224,7 @@ In `--thorough` mode, document conflicts AND flag as BLOCKING until user confirm
 Always persist the security audit after completing it:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. Summarize the security grade, finding counts by severity, and any critical decisions.
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -31,7 +31,7 @@ If either reports errors, fix them before proceeding. Warnings are informational
 **Verify review findings were resolved:**
 
 ```bash
-~/.claude/skills/nanostack/bin/find-artifact.sh review 2
+bin/find-artifact.sh review 2
 ```
 
 If a review artifact exists, check that all **blocking** findings have been addressed. For each blocking finding, verify the code at the reported file and line no longer has the issue. If a blocking finding is still present, do NOT proceed. Flag it.
@@ -186,8 +186,8 @@ Before creating the PR, verify these standards. The public repo is the face of t
 After shipping, persist the result and generate the sprint journal:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, open_questions>'
-~/.claude/skills/nanostack/bin/sprint-journal.sh
+bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/sprint-journal.sh
 ```
 
 The `context_checkpoint` is mandatory. Summarize what was shipped, PR number, and CI status.
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -159,7 +159,7 @@ Ready for: /nano
 Always persist the think output after the handoff brief:
 
 ```bash
-~/.claude/skills/nanostack/bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint including summary, key_files, decisions_made, open_questions>'
+bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint including summary, key_files, decisions_made, open_questions>'
 ```
 
 The `context_checkpoint` is mandatory. It captures the essence of this phase so downstream phases can restore context without replaying the full conversation. Write a 1-2 sentence summary, list key files, and document decisions made.
PATCH

echo "Gold patch applied."
