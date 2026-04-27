#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "1. **Check for contextual overrides first.** Look at the user's original prompt," "plugins/compound-engineering/skills/ce-debug/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-debug/SKILL.md b/plugins/compound-engineering/skills/ce-debug/SKILL.md
@@ -186,7 +186,7 @@ If the user chose "Diagnosis only" at the end of Phase 2, skip this phase and go
 **Conditional defense-in-depth** (trigger: grep for the root-cause pattern found it in 3+ other files, OR the bug would have been catastrophic if it reached production): Read `references/defense-in-depth.md` for the four-layer model (entry validation, invariant check, environment guard, diagnostic breadcrumb) and choose which layers apply. Skip when the root cause is a one-off error with no realistic recurrence path.
 
 **Conditional post-mortem** (trigger: the bug was in production, OR the pattern appears in 3+ locations):
-How was this introduced? What allowed it to survive? If a systemic gap was found: "This pattern appears in N other files. Want to capture it with `/ce-compound`?"
+Analyze how this was introduced and what allowed it to survive. Note any systemic gap or repeated pattern found — it informs Phase 4's decision on whether to offer learning capture.
 
 ---
 
@@ -206,13 +206,30 @@ How was this introduced? What allowed it to survive? If a systemic gap was found
 
 **If Phase 3 was skipped** (user chose "Diagnosis only" in Phase 2), stop after the summary — the user already told you they were taking it from here. Do not prompt.
 
-**If Phase 3 ran**, immediately after the summary prompt the user for the next action via the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini, `ask_user` in Pi (requires the `pi-ask-user` extension)). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded — a pending schema load is not a reason to fall back. Fall back to numbered options in chat only when no blocking tool exists in the harness or the call errors (e.g., Codex edit modes). Never end the phase without collecting a response — do not stop at "ready when you are" or any other passive phrasing that leaves the user hanging.
+**If Phase 3 ran**, the next move depends on whether the skill created the branch in Phase 3.
 
-Options (include only those that apply):
+#### Skill-owned branch (created in Phase 3): default to commit-and-PR without prompting
 
-1. **Commit the fix (`/ce-commit`)** — stage and commit the change locally (always applies here, since Phase 3 ran)
-2. **Commit and open a PR (`/ce-commit-push-pr`)** — commit, push, and open a pull request
-3. **Document as a learning first (`/ce-compound`)** — capture the bug and fix as a reusable pattern
-4. **Post findings to the issue first** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came from an issue tracker)
+1. **Check for contextual overrides first.** Look at the user's original prompt, loaded memories, and the user/repo `AGENTS.md` or `CLAUDE.md` for preferences that conflict with auto commit-and-PR — for example, "always review before pushing", "open PRs as drafts", or "don't open PRs from skills". A signal must be an explicit instruction or a clearly applicable rule, not a vague tonal cue. If any apply, honor them — switch to the pre-existing-branch menu below, or skip the PR step entirely, whichever matches the user's stated preference.
+2. **Briefly preview what will happen** — what will be committed, on what branch, and that a PR will be opened — then proceed without waiting for confirmation. The preview exists so the user can interrupt; it is not a blocking question. Format and length are your call; keep it scannable.
+3. **Run `/ce-commit-push-pr`.** When the entry came from an issue tracker, include the appropriate auto-close syntax for that tracker in the location it requires — most trackers parse PR descriptions (e.g., `Fixes #N` for GitHub, `Closes ABC-123` for Linear), but some only parse commit messages (e.g., Jira Smart Commits) — so the diagnosis and fix flow back to the issue and it closes on merge. Surface the resulting PR URL.
 
-Options 1 and 2 are terminal — running either ends the skill. Options 3 and 4 are additive: after the chosen action completes, re-prompt with the remaining options (excluding the one just completed and any that no longer apply).
+#### Pre-existing branch (skill did not create it): ask the user
+
+Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini, `ask_user` in Pi (requires the `pi-ask-user` extension)). In Claude Code, call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded — a pending schema load is not a reason to fall back. Fall back to numbered options in chat only when no blocking tool exists in the harness or the call errors. Never end the phase without collecting a response.
+
+Options:
+
+1. **Commit and open a PR (`/ce-commit-push-pr`)** — default for most cases
+2. **Commit the fix (`/ce-commit`)** — local commit only
+3. **Stop here** — user takes it from there
+
+#### After a PR is open (either path): consider offering learning capture
+
+Most bugs are localized mechanical fixes (typo, missed null check, missing import) where the only "lesson" is the bug itself. Compounding those clutters `docs/solutions/` without adding value. Decide which path applies:
+
+- **Skip silently** when the fix is mechanical and there's no generalizable insight. Default to this when in doubt.
+- **Offer neutrally** when the lesson can be stated in one sentence — e.g., "X.foo() returns T | undefined when Y, not just T", or "the diagnostic path was non-obvious and worth recording." If you cannot articulate the lesson, skip rather than offer.
+- **Lean into the offer** when the pattern appears in 3+ locations OR the root cause reveals a wrong assumption about a shared dependency, framework, or convention that other code is likely to repeat.
+
+When offering, use the blocking question tool described above. If the user accepts, run `/ce-compound`, then commit the resulting learning doc to the same branch and push so the open PR picks up the new commit.
PATCH

echo "Gold patch applied."
