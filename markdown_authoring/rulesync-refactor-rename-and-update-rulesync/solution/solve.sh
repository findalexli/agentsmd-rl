#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rulesync

# Idempotency guard
if grep -qF "10. Create a **draft** release using `gh release create v${new_version} --draft " ".rulesync/skills/draft-release/SKILL.md" && grep -qF "name: post-review-comments" ".rulesync/skills/post-review-comments/SKILL.md" && grep -qF ".rulesync/skills/release/SKILL.md" ".rulesync/skills/release/SKILL.md" && grep -qF "Using the review results from Step 1, run the `post-review-comments` skill with " ".rulesync/skills/review-and-comments/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.rulesync/skills/draft-release/SKILL.md b/.rulesync/skills/draft-release/SKILL.md
@@ -0,0 +1,31 @@
+---
+name: draft-release
+description: "Draft a new release of the project."
+targets:
+  - "*"
+---
+
+First, let's work on the following steps.
+
+1. Confirm that you are currently on the main branch and pull the latest changes. If not on main branch, switch to main branch.
+2. Compare code changes between the previous version tag and the latest commit to prepare the release description.
+
+- Write in English.
+- Do not include confidential information.
+- Sections, `What's Changed`, `Contributors` and `Full Changelog` are needed.
+- `./tmp/release-notes/*.md` will be used as the release notes.
+
+Then, from $ARGUMENTS, get the new version without v prefix, and assign it to $new_version. For example, if $ARGUMENTS is "v1.0.0", the new version is "1.0.0".
+
+If $ARGUMENTS is empty, determine the new version automatically by performing the `release-dry-run` skill.
+
+Let's resume the release process.
+
+3. Run `git pull`.
+4. Run `git checkout -b release/v${new_version}`.
+5. Update `getVersion()` function to return the ${new_version} in `src/cli/index.ts`, and run `pnpm cicheck`. If the checks fail, fix the code until pass. Then, execute `git add`, `git commit` and `git push`.
+6. Update the version with `pnpm version ${new_version} --no-git-tag-version`.
+7. Since `package.json` will be modified, execute `git commit` and `git push`.
+8. As a precaution, verify that `getVersion()` in `src/cli/index.ts` is updated to the ${new_version}.
+9. Run `gh pr create` to the main branch.
+10. Create a **draft** release using `gh release create v${new_version} --draft --title v${new_version} --notes-file ./tmp/release-notes/*.md` command on the `github.com/dyoshikawa/rulesync` repository. This creates a draft release so that the publish-assets workflow can upload assets later.
diff --git a/.rulesync/skills/post-review-comments/SKILL.md b/.rulesync/skills/post-review-comments/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: post-review-comment
+name: post-review-comments
 description: >-
   Post line-level review comments and an overall review comment on a PR in
   English with a natural, concise writing style
diff --git a/.rulesync/skills/release/SKILL.md b/.rulesync/skills/release/SKILL.md
@@ -1,34 +0,0 @@
----
-name: release
-description: "Release a new version of the project."
-targets:
-  - "*"
----
-
-First, let's work on the following steps.
-
-1. Confirm that you are currently on the main branch. If not on main branch, abort this operation.
-2. Compare code changes between the previous version tag and the latest commit to prepare the release description.
-
-- Write in English.
-- Do not include confidential information.
-- Sections, `What's Changed`, `Contributors` and `Full Changelog` are needed.
-- `./ai-tmp/release-notes.md` will be used as the release notes.
-
-Then, from $ARGUMENTS, get the new version without v prefix, and assign it to $new_version. For example, if $ARGUMENTS is "v1.0.0", the new version is "1.0.0".
-
-Unless the user does not explicitly specify the new version, please judge the new version from the release description with the following the general semantic versioning rules.
-
-Let's resume the release process.
-
-3. Run `git pull`.
-4. Run `git checkout -b release/v${new_version}`.
-5. Update `getVersion()` function to return the ${new_version} in `src/cli/index.ts`, and run `pnpm cicheck:code`. If the checks fail, fix the code until pass. Then, execute `git add` and `git commit`.
-6. Update the version with `pnpm version ${new_version} --no-git-tag-version`.
-7. Since `package.json` will be modified, execute `git commit` and `git push`.
-8. Run `gh pr create` and `gh pr merge --admin` to merge the release branch into the main branch.
-9. As a precaution, verify that `getVersion()` in `src/cli/index.ts` is updated to the ${new_version}.
-10. Create a **draft** release using `gh release create v${new_version} --draft --title v${new_version} --notes-file ./ai-tmp/release-notes.md` command on the `github.com/dyoshikawa/rulesync` repository. This creates a draft release so that the publish-assets workflow can upload assets.
-11. Wait for the publish-assets workflow to complete successfully. Use `gh run list --workflow="Publish Assets" --branch v${new_version} --limit 1 --json status,conclusion,databaseId` to check the status. Poll until the workflow completes (status is "completed"). If it fails, abort the release process and report the failure.
-12. Once the publish-assets workflow succeeds, publish the release by running `gh release edit v${new_version} --draft=false`.
-13. Clean up the branches. Run `git checkout main`, `git branch -D release/v${new_version}` and `git pull --prune`.
diff --git a/.rulesync/skills/review-and-comments/SKILL.md b/.rulesync/skills/review-and-comments/SKILL.md
@@ -0,0 +1,20 @@
+---
+name: review-and-comments
+description: >-
+  Review a PR for code quality and security issues, then post review comments on
+  it. Runs review-pr followed by post-review-comments sequentially.
+targets:
+  - "*"
+---
+
+target_pr = $ARGUMENTS
+
+If target_pr is not provided, use the PR of the current branch.
+
+## Step 1: Review the PR
+
+Run the `review-pr` skill with $target_pr.
+
+## Step 2: Post Review Comments
+
+Using the review results from Step 1, run the `post-review-comments` skill with $target_pr.
PATCH

echo "Gold patch applied."
