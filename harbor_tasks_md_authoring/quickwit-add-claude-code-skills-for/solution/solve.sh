#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quickwit

# Idempotency guard
if grep -qF "gh pr create --title \"Bump tantivy to {short-sha}\" --body \"Updates tantivy depen" ".claude/skills/bump-tantivy/SKILL.md" && grep -qF "Verify that all changes have been staged (no unstaged changes). If there are uns" ".claude/skills/simple-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/bump-tantivy/SKILL.md b/.claude/skills/bump-tantivy/SKILL.md
@@ -0,0 +1,83 @@
+---
+name: bump-tantivy
+description: Bump tantivy to the latest commit on main branch, fix compilation issues, and open a PR
+disable-model-invocation: true
+---
+
+# Bump Tantivy
+
+Follow these steps to bump tantivy to its latest version:
+
+## Step 1: Check that we are on the main branch
+
+Run: `git branch --show-current`
+
+If the current branch is not `main`, abort and ask the user to switch to the main branch first.
+
+## Step 2: Ensure main is up to date
+
+Run: `git pull origin main`
+
+This ensures we're working from the latest code.
+
+## Step 3: Get the latest tantivy SHA
+
+Run: `gh api repos/quickwit-oss/tantivy/commits/main --jq '.sha'`
+
+Extract the first 7 characters as the short SHA.
+
+## Step 4: Update Cargo.toml
+
+Edit `quickwit/Cargo.toml` and update the `rev` field in the tantivy dependency to the new short SHA.
+
+The line looks like:
+```toml
+tantivy = { git = "https://github.com/quickwit-oss/tantivy/", rev = "XXXXXXX", ... }
+```
+
+## Step 5: Run cargo check and fix compilation errors
+
+Run `cargo check` in the `quickwit` directory to verify compilation.
+
+If there are compilation errors:
+- If the fix is straightforward (simple API changes, renames, etc.), fix them without asking
+- If the fix is complex or unclear, ask the user before proceeding
+
+Repeat until cargo check passes.
+
+## Step 6: Format code
+
+Run `make fmt` from the `quickwit/` directory to format the code.
+
+## Step 7: Update licenses
+
+Run `make update-licenses` from the `quickwit/` directory, then move the generated file:
+```
+mv quickwit/LICENSE-3rdparty.csv ./LICENSE-3rdparty.csv
+```
+
+## Step 8: Create a new branch
+
+Get the git username: `git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]'`
+
+Get today's date: `date +%Y-%m-%d`
+
+Create and checkout a new branch named: `{username}/bump-tantivy-{date}`
+
+Example: `paul/bump-tantivy-2024-03-15`
+
+## Step 9: Commit changes
+
+Stage all modified files and create a commit with message:
+```
+Bump tantivy to {short-sha}
+```
+
+## Step 10: Push and open a PR
+
+Push the branch and open a PR using:
+```
+gh pr create --title "Bump tantivy to {short-sha}" --body "Updates tantivy dependency to the latest commit on main."
+```
+
+Report the PR URL to the user when complete.
diff --git a/.claude/skills/simple-pr/SKILL.md b/.claude/skills/simple-pr/SKILL.md
@@ -0,0 +1,60 @@
+---
+name: simple-pr
+description: Create a simple PR from staged changes with an auto-generated commit message
+disable-model-invocation: true
+---
+
+# Simple PR
+
+Follow these steps to create a simple PR from staged changes:
+
+## Step 1: Check workspace state
+
+Run: `git status`
+
+Verify that all changes have been staged (no unstaged changes). If there are unstaged changes, abort and ask the user to stage their changes first with `git add`.
+
+Also verify that we are on the `main` branch. If not, abort and ask the user to switch to main first.
+
+## Step 2: Ensure main is up to date
+
+Run: `git pull origin main`
+
+This ensures we're working from the latest code.
+
+## Step 3: Review staged changes
+
+Run: `git diff --cached`
+
+Review the staged changes to understand what the PR will contain.
+
+## Step 4: Generate commit message
+
+Based on the staged changes, generate a concise commit message (1-2 sentences) that describes the "why" rather than the "what".
+
+Display the proposed commit message to the user and ask for confirmation before proceeding.
+
+## Step 5: Create a new branch
+
+Get the git username: `git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]'`
+
+Create a short, descriptive branch name based on the changes (e.g., `fix-typo-in-readme`, `add-retry-logic`, `update-deps`).
+
+Create and checkout the branch: `git checkout -b {username}/{short-descriptive-name}`
+
+## Step 6: Commit changes
+
+Commit with the message from step 3:
+```
+git commit -m "{commit-message}"
+```
+
+## Step 7: Push and open a PR
+
+Push the branch and open a PR:
+```
+git push -u origin {branch-name}
+gh pr create --title "{commit-message-title}" --body "{longer-description-if-needed}"
+```
+
+Report the PR URL to the user when complete.
PATCH

echo "Gold patch applied."
