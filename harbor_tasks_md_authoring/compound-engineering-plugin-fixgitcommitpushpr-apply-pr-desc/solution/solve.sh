#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "2. Apply the returned title and body file yourself. This is this skill's respons" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -80,11 +80,14 @@ If `ce-pr-description` returns a "not open" or other graceful-exit message inste
 - If the user provided a focus, confirm it was addressed.
 - Ask the user to confirm before applying.
 
-If confirmed, apply with the returned title and body file:
+**If confirmed, perform these two actions in order.** They are separate steps with a hand-off boundary between them — do not stop after action 1.
 
-```bash
-gh pr edit --title "<returned title>" --body "$(cat "<returned body_file>")"
-```
+1. `ce-pr-description` has already returned its `=== TITLE ===` / `=== BODY_FILE ===` block and stopped; it does not apply on its own.
+2. Apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` contains `"`, `` ` ``, `$`, or `\`, escape them or switch to single quotes:
+
+   ```bash
+   gh pr edit --title "<TITLE>" --body "$(cat "<BODY_FILE>")"
+   ```
 
 Report the PR URL.
 
@@ -210,10 +213,10 @@ If `ce-pr-description` returns a graceful-exit message instead of `{title, body_
 
 #### New PR (no existing PR from Step 3)
 
-Using the `{title, body_file}` returned by `ce-pr-description`:
+Using the `=== TITLE ===` / `=== BODY_FILE ===` block returned by `ce-pr-description`, substitute `<TITLE>` and `<BODY_FILE>` verbatim. If `<TITLE>` contains `"`, `` ` ``, `$`, or `\`, escape them or switch to single quotes:
 
 ```bash
-gh pr create --title "<returned title>" --body "$(cat "<returned body_file>")"
+gh pr create --title "<TITLE>" --body "$(cat "<BODY_FILE>")"
 ```
 
 Keep the title under 72 characters; `ce-pr-description` already emits a conventional-commit title in that range.
@@ -222,13 +225,16 @@ Keep the title under 72 characters; `ce-pr-description` already emits a conventi
 
 The new commits are already on the PR from Step 5. Report the PR URL, then ask whether to rewrite the description.
 
-- If **yes**, run Step 6 now to generate `{title, body_file}` via `ce-pr-description` (passing the existing PR URL as `pr:`), then apply the returned title and body file:
+- If **no** -- skip Step 6 entirely and finish. Do not run delegation or evidence capture when the user declined the rewrite.
+- If **yes**, perform these two actions in order. They are separate steps with a hand-off boundary between them -- do not stop after action 1.
+  1. Run Step 6 to generate via `ce-pr-description` (passing the existing PR URL as `pr:`). `ce-pr-description` explicitly does not apply on its own; it returns its `=== TITLE ===` / `=== BODY_FILE ===` block and stops.
+  2. Apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block; if `<TITLE>` contains `"`, `` ` ``, `$`, or `\`, escape them or switch to single quotes:
 
-  ```bash
-  gh pr edit --title "<returned title>" --body "$(cat "<returned body_file>")"
-  ```
+     ```bash
+     gh pr edit --title "<TITLE>" --body "$(cat "<BODY_FILE>")"
+     ```
 
-- If **no** -- skip Step 6 entirely and finish. Do not run delegation or evidence capture when the user declined the rewrite.
+  Then report the PR URL (Step 8).
 
 ### Step 8: Report
 
PATCH

echo "Gold patch applied."
