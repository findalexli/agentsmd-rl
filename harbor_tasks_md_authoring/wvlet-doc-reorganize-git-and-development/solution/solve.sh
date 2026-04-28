#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wvlet

# Idempotency guard
if grep -qF "- Gemini will review pull requests for code quality, adherence to guidelines, an" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -200,7 +200,13 @@ test _.output should be """
 
 The project follows semantic versioning and uses SBT plugins for cross-platform publishing. Check `project/release.rb` for release automation scripts.
 
-## Git and Development Workflow
+## Git & Development Workflow
+
+### Development Process
+- **Before addressing a new task, switch to main and pull, and then create a new branch**
+- Create a new branch and create a pull request for code development
+- In git worktree environment, create a new branch based on origin/main
+- **Before making changes, always create a new branch for pull request**
 
 ### Branching
 - Create descriptive branches with timestamp for uniqueness
@@ -216,22 +222,27 @@ The project follows semantic versioning and uses SBT plugins for cross-platform
 - Focus on "why" rather than "what" or "how"
 - Good example: `feature: Add XXX to improve user experience`
 - Avoid: `feature: Add XXX class`
+- **Include CLAUDE.md changes as needed to the commit**
+  - If modifying project structure, development processes, or adding new guidelines, update this file
+  - Ensure the guidance remains clear, concise, and helpful for developers
 
 ### Pull Requests
 - Use [`gh pr create`](https://cli.github.com/manual/gh_pr_create) with clear title and detailed body
 - Follow .github/pull_request_template.md format
 - Merge with squash via `gh pr merge --squash --auto` for clean history
+- Check PR status and fix issues like code format, compilation failure, test failures
+- After merging PR, update the related issues to reflect completed and remaining tasks
+- **After PR is merged, switch to main branch and pull to get latest changes**
 
 ### Code Reviews
+- Gemini will review pull requests for code quality, adherence to guidelines, and test coverage. Reflect on feedback and make necessary changes
+- After creating a PR, wait for review from Gemini for a while, and reflect on the suggestions, and update the PR
+- To ask Gemini review the code change again, comment `/gemini review` to the pull request
 
-- Gemini will review pull requests for code quality, adherence to guidelines, and test coverage. Reflect on feedback and make necessary changes.
-- After creating a PR, wait for review from Gemini for a while, and reflect on the suggestions, and update the PR.
-- To ask Gemini review the code change again, comment `/gemini review` to the pull request 
-
-### Development Workflow
-
-- To develop a code, create a new branch and create a pull request
-- **Before addressing a new task, switch to main and pull, and then create a new branch**
+### GitHub CLI Commands
+- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`
+- Check PR status: `gh pr status`
+- View PR checks: `gh pr checks PR_NUMBER`
 
 ## Error Handling
 
@@ -244,23 +255,10 @@ For error reporting, use WvletLangException and StatusCode enum. If necessary er
 ## Development Checklist
 - Before commiting changes, confirm compilation passes for src/main, src/test, and Scala.js
 
-## Commit Guidance
-
-- **Include CLAUDE.md changes as needed to the commit**
-  - If modifying project structure, development processes, or adding new guidelines, update this file
-  - Ensure the guidance remains clear, concise, and helpful for developers
-
 ## Memory
-- In git worktree environment, create a new branch based on origin/main
 - For creating temporary files, use target folder, which will be ignored in git
-- **Before making changes, always create a new branch for pull request**
 - `vscode-wvlet` is VS Code plugin folder
 
-## Workflow for PR Checks
-
-- Check pr status and fix issues like code format, compilation failure, test failures
-- After merging pr, updated the related issues to reflect completed and remaining tasks
-
 ## CI Optimization
 
 ### Python SDK Testing
@@ -275,10 +273,3 @@ For error reporting, use WvletLangException and StatusCode enum. If necessary er
 - Use `shouldContain "(keyword)"` for checking string fragment in AirSpec
 - To debug SQL generator, add -L *GenSQL=trace to the test option
 
-## GitHub CLI Commands
-
-### Pull Request Management
-- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`
-- Check PR status: `gh pr status`
-- View PR checks: `gh pr checks PR_NUMBER`
-- Merge PR: `gh pr merge --squash --auto`
\ No newline at end of file
PATCH

echo "Gold patch applied."
