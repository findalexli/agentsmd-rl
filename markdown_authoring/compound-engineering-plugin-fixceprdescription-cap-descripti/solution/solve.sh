#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "2. **Preview and confirm.** Read the first two sentences of the Summary from the" "plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md" && grep -qF "**In Claude Code**, the five labeled sections below (Git status, Working tree di" "plugins/compound-engineering/skills/ce-commit/SKILL.md" && grep -qF "| Large or architecturally significant | Narrative frame + up to 3-5 design-deci" "plugins/compound-engineering/skills/ce-pr-description/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md
@@ -17,9 +17,9 @@ For description-only updates, follow the Description Update workflow below. Othe
 
 ## Context
 
-**If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
+**On platforms other than Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
 
-**If you are Claude Code**, the six labeled sections below contain pre-populated data. Use them directly -- do not re-run these commands.
+**In Claude Code**, the six labeled sections below contain pre-populated data. Use them directly -- do not re-run these commands.
 
 **Git status:**
 !`git status`
@@ -41,7 +41,7 @@ For description-only updates, follow the Description Update workflow below. Othe
 
 ### Context fallback
 
-**If you are Claude Code, skip this section — the data above is already available.**
+**In Claude Code, skip this section — the data above is already available.**
 
 Run this single command to gather all context:
 
@@ -205,6 +205,8 @@ When evidence is not possible (docs-only, markdown-only, changelog-only, release
 - **For a new PR** (no existing PR found in Step 3): invoke with `base:<base-remote>/<base-branch>` using the already-resolved base from earlier in this step, so `ce-pr-description` describes the correct commit range even when the branch targets a non-default base (e.g., `develop`, `release/*`). Append any captured-evidence context or user focus as free-text steering (e.g., "include the captured demo: <URL> as a `## Demo` section").
 - **For an existing PR** (found in Step 3): invoke with the full PR URL from the Step 3 context (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when invoked from a worktree or subdirectory; the skill reads the PR's own `baseRefName` so no `base:` override is needed. Append any focus steering as free text after the URL.
 
+**Steering discipline.** Pass only what the diff cannot reveal: a user focus ("emphasize the performance win"), a specific framing concern ("this needs to read as a migration not a feature"), or a pointer to institutional knowledge. Do NOT dump an exhaustive scope summary or a numbered list of every change — `ce-pr-description` reads the diff itself. Over-specified steering encourages the downstream skill to cover everything passed in, producing verbose output. Cap steering at roughly 100 words; if a longer framing feels necessary, trust the diff and cut.
+
 `ce-pr-description` returns a `{title, body_file}` block (body in an OS temp file). It applies the value-first writing principles, commit classification, sizing, narrative framing, writing voice, visual communication, numbering rules, and the Compound Engineering badge footer internally. Use the returned values verbatim in Step 7; do not layer manual edits onto them unless a focused adjustment is required (e.g., splicing an evidence block captured in this step that was not passed as steering text — in that case, edit the body file directly before applying).
 
 If `ce-pr-description` returns a graceful-exit message instead of `{title, body_file}` (e.g., closed PR, no commits to describe, base ref unresolved), report the message and stop — do not create or edit the PR.
@@ -226,9 +228,10 @@ Keep the title under 72 characters; `ce-pr-description` already emits a conventi
 The new commits are already on the PR from Step 5. Report the PR URL, then ask whether to rewrite the description.
 
 - If **no** -- skip Step 6 entirely and finish. Do not run delegation or evidence capture when the user declined the rewrite.
-- If **yes**, perform these two actions in order. They are separate steps with a hand-off boundary between them -- do not stop after action 1.
+- If **yes**, perform these three actions in order. They are separate steps with a hand-off boundary between them -- do not stop between actions.
   1. Run Step 6 to generate via `ce-pr-description` (passing the existing PR URL as `pr:`). `ce-pr-description` explicitly does not apply on its own; it returns its `=== TITLE ===` / `=== BODY_FILE ===` block and stops.
-  2. Apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` contains `"`, `` ` ``, `$`, or `\`, escape them or switch to single quotes:
+  2. **Preview and confirm.** Read the first two sentences of the Summary from the body file, plus the total line count. Ask the user (per the "Asking the user" convention at the top of this skill): "New title: `<title>` (`<N>` chars). Summary leads with: `<first two sentences>`. Total body: `<L>` lines. Apply?" The first two sentences of the Summary carry most of the reviewer's attention; they are the single highest-leverage text in the description, so they are what the preview spotlights. If the user declines, they may pass steering text back for a regenerate; do not apply.
+  3. If confirmed, apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` contains `"`, `` ` ``, `$`, or `\`, escape them or switch to single quotes:
 
      ```bash
      gh pr edit --title "<TITLE>" --body "$(cat "<BODY_FILE>")"
diff --git a/plugins/compound-engineering/skills/ce-commit/SKILL.md b/plugins/compound-engineering/skills/ce-commit/SKILL.md
@@ -9,9 +9,9 @@ Create a single, well-crafted git commit from the current working tree changes.
 
 ## Context
 
-**If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
+**On platforms other than Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
 
-**If you are Claude Code**, the five labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch) contain pre-populated data. Use them directly throughout this skill -- do not re-run these commands.
+**In Claude Code**, the five labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch) contain pre-populated data. Use them directly throughout this skill -- do not re-run these commands.
 
 **Git status:**
 !`git status`
@@ -30,7 +30,7 @@ Create a single, well-crafted git commit from the current working tree changes.
 
 ### Context fallback
 
-**If you are Claude Code, skip this section — the data above is already available.**
+**In Claude Code, skip this section — the data above is already available.**
 
 Run this single command to gather all context:
 
diff --git a/plugins/compound-engineering/skills/ce-pr-description/SKILL.md b/plugins/compound-engineering/skills/ce-pr-description/SKILL.md
@@ -86,20 +86,20 @@ if [ -z "$CURRENT_BRANCH" ]; then
   exit 1
 fi
 
-# Priority: caller-supplied base: > existing PR's baseRefName > origin/HEAD
+# Priority: caller-supplied base: > existing PR's baseRefName > origin/HEAD > origin/main
 if [ -n "$CALLER_BASE" ]; then
   BASE_REF="$CALLER_BASE"
+elif EXISTING_PR_BASE=$(gh pr view --json baseRefName --jq '.baseRefName'); then
+  BASE_REF="origin/$EXISTING_PR_BASE"
+elif DEFAULT_HEAD=$(git rev-parse --abbrev-ref origin/HEAD); then
+  BASE_REF="$DEFAULT_HEAD"
 else
-  EXISTING_PR_BASE=$(gh pr view --json baseRefName --jq '.baseRefName' 2>/dev/null)
-  if [ -n "$EXISTING_PR_BASE" ]; then
-    BASE_REF="origin/$EXISTING_PR_BASE"
-  else
-    BASE_REF=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null)
-    BASE_REF="${BASE_REF:-origin/main}"
-  fi
+  BASE_REF="origin/main"
 fi
 ```
 
+Both `gh pr view` and `git rev-parse --abbrev-ref origin/HEAD` exit non-zero on the "not configured" paths; the elif chain drives off exit code rather than suppressed stderr. Stderr from a missing PR or unresolved `origin/HEAD` is informational and acceptable.
+
 If `$BASE_REF` does not resolve locally (`git rev-parse --verify "$BASE_REF"` fails), the caller (or the user) needs to fetch it first. Exit gracefully with `"Base ref $BASE_REF does not resolve locally. Fetch it before invoking the skill."` — do not attempt recovery.
 
 Gather merge base, commit list, and full diff:
@@ -216,10 +216,10 @@ Assess size (files, diff volume) and complexity (design decisions, trade-offs, c
 | Small + simple (typo, config, dep bump) | 1-2 sentences, no headers. Under ~300 characters. |
 | Small + non-trivial (bugfix, behavioral change) | Short narrative, ~3-5 sentences. No headers unless two distinct concerns. |
 | Medium feature or refactor | Narrative frame (before/after/scope), then what changed and why. Call out design decisions. |
-| Large or architecturally significant | Full narrative: problem context, approach (and why), key decisions, migration/rollback if relevant. |
+| Large or architecturally significant | Narrative frame + up to 3-5 design-decision callouts + 1-2 sentence test summary + key docs links. Target ~100 lines, cap ~150. For PRs with many mechanisms, use a Summary-level table to list them; do NOT create an H3 subsection per mechanism. Reviewers scrutinize decisions, not inventories — the diff and spec files carry the detail. If you find yourself writing 10+ subsections, consolidate to a table. |
 | Performance improvement | Include before/after measurements if available. Markdown table works well. |
 
-When in doubt, shorter is better. Match description weight to change weight.
+When in doubt, shorter is better. Match description weight to change weight. Large PRs need MORE selectivity, not MORE content.
 
 ---
 
@@ -247,6 +247,8 @@ If the repo has documented style preferences in context, follow those. Otherwise
 - **Markdown tables for data**: Before/after comparisons, performance numbers, or option trade-offs communicate well as tables.
 - **No empty sections**: If a section doesn't apply, omit it. No "N/A" or "None."
 - **Test plan — only when non-obvious**: Include when testing requires edge cases the reviewer wouldn't think of, hard-to-verify behavior, or specific setup. Omit when "run the tests" is the only useful guidance. When the branch adds test files, name them with what they cover.
+- **No Commits section**: GitHub already shows the commit list in its own tab. A Commits section in the PR body duplicates that without adding context. Omit unless the commits need annotations explaining their ordering or shipping rationale.
+- **No Review / process section**: Do not include a section describing how the reviewer should review (checklists of things to look at, process bullets). Process doesn't help the reviewer evaluate code. Call out specific non-obvious things to scrutinize inline with the change that warrants it.
 
 ### Visual communication
 
@@ -344,6 +346,23 @@ Assemble the body in this order:
 
 ---
 
+## Step 8b: Compression pass
+
+Before writing the body to the temp file, re-read the composed body and apply these cuts:
+
+- If any body section restates content already in the `## Summary`, remove it. The Summary plus the diff should carry the reader.
+- If "Testing" or "Test plan" has more than 2 paragraphs, compress to bullets.
+- If a "Commits" section enumerates the commit log, remove it — GitHub shows it in its own tab.
+- If a "Review" or process-oriented section lists how to review, remove it. Move any truly non-obvious review hints inline with the relevant change.
+- If the body has 5+ H3 subsections that each describe one mechanism, consolidate them into a single table row per mechanism under one header. Reserve prose H3 callouts for 2-3 genuine design decisions.
+- If the body exceeds the sizing-table target by more than 30%, compress the longest non-Summary section by half.
+
+**Value-lead check.** Re-read the first sentence of the Summary. If it describes what was moved around, renamed, or added ("This PR introduces three-tier autofix..."), rewrite to lead with what's now possible or what was broken and is now fixed ("Document reviews previously produced 14+ findings requiring user judgment; this PR cuts that to 4-6.").
+
+Large PRs benefit from selectivity, not comprehensiveness.
+
+---
+
 ## Step 9: Return `{title, body_file}`
 
 Write the composed body to an OS temp file, then return the title and the file path. Do not call `gh pr edit`, `gh pr create`, or any other mutating command. Do not ask the user to confirm — the caller owns apply.
@@ -370,7 +389,7 @@ Do not emit the body markdown in the return block — the caller reads it from `
 
 If Step 1 exited gracefully (closed/merged PR, invalid range, empty commit list), do not create a body file — just return the reason string.
 
-**The return block is a hand-off, not task completion.** When invoked by a parent skill (e.g., `git-commit-push-pr`), emit the return block and then continue executing the parent's remaining steps (typically `gh pr create` or `gh pr edit` with the returned title and body file). Do not stop after the return block unless invoked directly by the user with no parent workflow.
+**The return block is a hand-off, not task completion.** When invoked by a parent skill (e.g., `ce-commit-push-pr`), emit the return block and then continue executing the parent's remaining steps (typically `gh pr create` or `gh pr edit` with the returned title and body file). Do not stop after the return block unless invoked directly by the user with no parent workflow.
 
 ---
 
PATCH

echo "Gold patch applied."
