#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Follow the \"Detect the base branch and remote\" and \"Gather the branch scope\" sec" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -81,7 +81,7 @@ Read the current PR description:
 gh pr view --json body --jq '.body'
 ```
 
-Follow the "Detect the base branch and remote" and "Gather the branch scope" sections of Step 6 to get the full branch diff. Use the PR found in DU-2 as the existing PR for base branch detection. Then write a new description following the writing principles in Step 6. If the user provided a focus, incorporate it into the description alongside the branch diff context.
+Follow the "Detect the base branch and remote" and "Gather the branch scope" sections of Step 6 to get the full branch diff. Use the PR found in DU-2 as the existing PR for base branch detection. Classify commits per the "Classify commits before writing" section -- this is especially important for description updates, where the recent commits that prompted the update are often fix-up work (code review fixes, lint fixes) rather than feature work. Then write a new description following the writing principles in Step 6, driven by the feature commits and the final diff. If the user provided a focus, incorporate it into the description alongside the branch diff context.
 
 Compare the new description against the current one and summarize the substantial changes for the user (e.g., "Added coverage of the new caching layer, updated test plan, removed outdated migration notes"). If the user provided a focus, confirm it was addressed. Ask the user to confirm before applying. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the summary and wait for the user's reply.
 
@@ -248,6 +248,15 @@ Once the base branch and remote are known:
 
 Use the full branch diff and commit list as the basis for the PR description -- not the working-tree diff from Step 1.
 
+#### Classify commits before writing
+
+Before writing the description, scan the commit list and classify each commit:
+
+- **Feature commits** -- implement the purpose of the PR (new functionality, intentional refactors, design changes). These drive the description.
+- **Fix-up commits** -- work product of getting the branch ready: code review fixes, lint/type error fixes, test fixes, rebase conflict resolutions, style cleanups, typo corrections in the new code. These are invisible to the reader.
+
+Only feature commits inform the description. Fix-up commits are noise -- they describe the iteration process, not the end result. The full diff already includes whatever the fix-up commits changed, so their intent is captured without narrating them. When sizing and writing the description, mentally subtract fix-up commits: a branch with 12 commits but 9 fix-ups is a 3-commit PR in terms of description weight.
+
 This is the most important step. The description must be **adaptive** -- its depth should match the complexity of the change. A one-line bugfix does not need a table of performance results. A large architectural change should not be a bullet list.
 
 #### Sizing the change
@@ -402,7 +411,7 @@ Keep the PR title under 72 characters. The title follows the same convention as
 
 The new commits are already on the PR from the push in Step 5. Report the PR URL, then ask the user whether they want the PR description updated to reflect the new changes. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the option and wait for the user's reply before proceeding.
 
-- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits), including the Compound Engineering badge unless one is already present in the existing description. Apply it:
+- If **yes** -- write a new description following the same principles in Step 6 (size the full PR, not just the new commits). Classify commits per "Classify commits before writing" -- the new commits since the last push are often fix-up work (code review fixes, lint fixes) and should not appear as distinct items in the updated description. Describe the PR's net result as if writing it fresh. Include the Compound Engineering badge unless one is already present in the existing description. Apply it:
 
   ```bash
   gh pr edit --body "$(cat <<'EOF'
PATCH

echo "Gold patch applied."
