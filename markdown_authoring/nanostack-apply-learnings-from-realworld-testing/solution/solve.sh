#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "- **Not reading CONTRIBUTING.md.** Every project has different rules. Some requi" "ship/SKILL.md" && grep -qF "- **Same intensity for everyone.** The first version challenged a user's persona" "think/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ship/SKILL.md b/ship/SKILL.md
@@ -46,9 +46,32 @@ git rebase origin/main  # preferred for clean history
 git merge origin/main   # if rebase would be messy
 ```
 
-### 2. Create PR
+### 2. PR Preview (mandatory stop)
 
-Use the template at `ship/templates/pr-template.md` for the PR body.
+Before creating the PR, show the user a full preview. This is a mandatory stop because after creation it's public.
+
+```
+## PR Preview
+
+**Title:** {{title}}
+**Branch:** {{branch}} → {{base}}
+**Files changed:** {{count}}
+
+### Summary
+{{1-3 bullets of what changed and why}}
+
+### Changes
+{{file list with one-line description each}}
+
+### Test plan
+{{how to verify}}
+```
+
+Wait for user approval. Only proceed after explicit confirmation. If the user adjusts something, update the preview and ask again.
+
+### 3. Create PR
+
+After approval, use the template at `ship/templates/pr-template.md` for the PR body.
 
 ```bash
 gh pr create \
@@ -70,7 +93,7 @@ EOF
 - Test plan: how to verify this works
 - Link to related issues/tickets
 
-### 3. Monitor CI
+### 4. Monitor CI
 
 After creating the PR, check CI status:
 
@@ -84,7 +107,7 @@ If CI fails:
 - Do not retry without understanding the failure
 - If a test is genuinely flaky (not caused by your change), note it in the PR
 
-### 4. Post-Merge Verification
+### 5. Post-Merge Verification
 
 After the PR is merged:
 
@@ -105,7 +128,7 @@ If the project has a staging/production URL, run a **post-deploy checklist:**
 
 If any check fails: **stop and rollback** before debugging. A broken prod is worse than a reverted feature.
 
-### 5. Rollback Plan
+### 6. Rollback Plan
 
 If something goes wrong after deploy:
 
@@ -117,7 +140,7 @@ gh pr create --title "Revert: {{original PR title}}" --body "Reverting due to {{
 
 Document what went wrong for the team.
 
-### 6. Repo Quality Standards
+### 7. Repo Quality Standards
 
 Before creating the PR, verify these standards. The public repo is the face of the project.
 
@@ -178,3 +201,13 @@ Include before/after test counts when tests were added during the sprint. Quanti
 - **Don't deploy on Friday afternoons.** Unless you want to debug on Saturday morning. If the user insists, note the risk.
 - **One PR = one concern.** If your PR does two unrelated things, split it. The review will be faster and the rollback will be cleaner.
 - **Draft PRs are useful.** If the code isn't ready for review but you want CI to run, create a draft: `gh pr create --draft`
+
+## Anti-patterns (from real usage)
+
+These were discovered from shipping real PRs:
+
+- **Creating PRs without checking existing work.** Submitted a PR to FastAPI without realizing 8 other PRs existed for the same issue, including one the maintainer preferred. Always search first.
+- **Skipping PR Preview.** A PR went out with "Fixes #4060" as the only body text. The project required What/Why/Before-After/Tests/AI disclosure. PR Preview catches this.
+- **Pushing directly to main.** Every change should go through a PR regardless of size. Clean history, reviewable changes.
+- **Not reading CONTRIBUTING.md.** Every project has different rules. Some require video evidence, some require specific naming conventions, some have line limits. Read the rules before writing the PR.
+- **CI checks that only maintainers resolve.** Label checks, CLA checks, approval gates. These will fail on your PR and there's nothing you can do. Know which checks you own and which you don't.
diff --git a/think/SKILL.md b/think/SKILL.md
@@ -48,6 +48,18 @@ Determine the mode from the user's description:
 
 **How to detect the mode:** If the user describes a personal pain ("I have this problem," "I need to..."), default to Startup or Builder. If the user pitches an idea for others ("I want to build X for Y market"), default to Startup. Only use Founder mode when the user asks for it or the context is clearly a high-stakes venture decision.
 
+### Phase 1.5: Search Before Building
+
+Before running the diagnostic, search for existing solutions. This is not optional.
+
+1. **Search for existing tools/libraries** that solve the problem. Use web search, GitHub search, npm/pip/go registries.
+2. **Search for prior art in the codebase** if working on an existing project. Someone may have started this work.
+3. **Check GitHub issues and PRs** if contributing to an open source project. Someone may have already submitted a fix or the maintainers may have stated a preferred approach.
+
+If an existing solution covers 80%+ of the need, recommend using it instead of building from scratch. "The best code is the code you don't write" is not a gotcha. It's the first check.
+
+Report what you found before proceeding to the diagnostic. If nothing exists, say so and move on.
+
 ### Phase 2: The Diagnostic
 
 #### Startup Mode — Six Forcing Questions
@@ -179,7 +191,16 @@ Wait for the user to invoke `/nano-plan`.
 - **Don't skip the diagnostic to "save time."** The diagnostic IS the time savings — it prevents building the wrong thing.
 - **Don't confuse conviction with evidence.** The user being excited about an idea is not validation. Who else is excited? Who would pay?
 - **Don't expand scope when reducing is the right call.** More features ≠ better product. The best v1s do one thing exceptionally well.
-- **"Search Before Building" is literal.** Before proposing to build anything, search for existing solutions. The best code is the code you don't write.
+- **"Search Before Building" is now a step, not a suggestion.** Phase 1.5 runs before the diagnostic. If you skipped it, go back.
 - **"Processize before you productize."** If the user can't describe how they'd deliver the value by hand (no code), they don't understand the problem well enough to automate it. The manual process comes first.
 - **Don't let this become a planning session.** /think produces a brief, not a plan. If you're writing implementation steps, you've gone too far. Hand off to /nano-plan.
 - **Don't let the user think small by habit.** An AI agent builds a web app as fast as a bash script. If the user defaults to "just a CLI" when a real product would serve them better, say so. The narrowest wedge should be narrow in scope, not narrow in ambition.
+
+## Anti-patterns (from real usage)
+
+These were discovered from running /think on real projects:
+
+- **Same intensity for everyone.** The first version challenged a user's personal pain point ("are your bookmarks even worth saving?"). Calibrate by mode. Founder mode pushes hard. Startup/Builder mode respects stated pain.
+- **Skipping Search Before Building.** A user wanted to build a feature that 3 other people had already submitted PRs for in the target repo. 30 seconds of search would have saved hours.
+- **Asking with AskUserQuestion when the user gave no context.** The modal prompt confused users. Just ask in plain text.
+- **Running the diagnostic on a problem that doesn't need a diagnostic.** "Fix this bug" doesn't need six forcing questions. Detect when the user already knows what they want and skip to the brief.
PATCH

echo "Gold patch applied."
