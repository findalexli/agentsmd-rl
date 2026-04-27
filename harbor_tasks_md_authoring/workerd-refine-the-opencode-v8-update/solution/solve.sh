#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotency guard
if grep -qF "**Never** take irreversible actions (like dropping patches or updating hashes) w" ".opencode/skills/update-v8/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/update-v8/SKILL.md b/.opencode/skills/update-v8/SKILL.md
@@ -9,6 +9,9 @@ V8 updates are high-risk changes that require careful patch management and human
 
 See also: `docs/v8-updates.md` for the original reference document.
 
+**Always** communicate and confirm with the developer at each step.
+**Never** take irreversible actions (like dropping patches or updating hashes) without explicit confirmation.
+
 ---
 
 ### Prerequisites
@@ -73,8 +76,6 @@ git rebase --onto <new_version> <old_version>
 - **Do not drop patches** without explicit confirmation from the developer.
 - **Do not auto-resolve conflicts** — flag them for human review. Merge conflicts in V8 patches almost always require human judgment.
 
-After rebasing, ideally build and test V8 standalone to verify patches apply cleanly. See the V8 [Testing](https://v8.dev/docs/test) page.
-
 ### Step 5: Regenerate patches
 
 ```sh
@@ -85,6 +86,9 @@ This produces numbered `.patch` files in the current directory.
 
 ### Step 6: Replace patches in workerd
 
+**Always** confirm with the human before replacing patches. If any patches were dropped or added,
+the human needs to review the changes.
+
 ```sh
 rm <path_to_workerd>/patches/v8/*
 cp *.patch <path_to_workerd>/patches/v8/
@@ -159,7 +163,11 @@ Watch for:
 
 ### Step 10: Commit and submit
 
-Commit the changes and push for review. The PR should include:
+Prompt the user to commit the changes and push for review.
+
+**Never** push the branch for review without a human review of the patch changes.
+
+You **May** prepare the draft PR text for the user. The PR should include:
 
 - Updated `build/deps/v8.MODULE.bazel` (version, integrity, patches list)
 - Updated patches in `patches/v8/`
PATCH

echo "Gold patch applied."
