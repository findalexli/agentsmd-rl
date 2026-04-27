#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "First, check whether the branch name is **meaningful** \u2014 a name like `feat/crowd" "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "First, check whether the branch name is **meaningful** \u2014 a name like `feat/crowd" "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -74,8 +74,17 @@ Determine how to proceed based on what was provided in `<input_document>`.
    ```
 
    **If already on a feature branch** (not the default branch):
-   - Ask: "Continue working on `[current_branch]`, or create a new branch?"
-   - If continuing, proceed to step 3
+
+   First, check whether the branch name is **meaningful** — a name like `feat/crowd-sniff` or `fix/email-validation` tells future readers what the work is about. Auto-generated worktree names (e.g., `worktree-jolly-beaming-raven`) or other opaque names do not.
+
+   If the branch name is meaningless or auto-generated, suggest renaming it before continuing:
+   ```bash
+   git branch -m <meaningful-name>
+   ```
+   Derive the new name from the plan title or work description (e.g., `feat/crowd-sniff`). Present the rename as a recommended option alongside continuing as-is.
+
+   Then ask: "Continue working on `[current_branch]`, or create a new branch?"
+   - If continuing (with or without rename), proceed to step 3
    - If creating new, follow Option A or B below
 
    **If on the default branch**, choose how to proceed:
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -73,8 +73,17 @@ Determine how to proceed based on what was provided in `<input_document>`.
    ```
 
    **If already on a feature branch** (not the default branch):
-   - Ask: "Continue working on `[current_branch]`, or create a new branch?"
-   - If continuing, proceed to step 3
+
+   First, check whether the branch name is **meaningful** — a name like `feat/crowd-sniff` or `fix/email-validation` tells future readers what the work is about. Auto-generated worktree names (e.g., `worktree-jolly-beaming-raven`) or other opaque names do not.
+
+   If the branch name is meaningless or auto-generated, suggest renaming it before continuing:
+   ```bash
+   git branch -m <meaningful-name>
+   ```
+   Derive the new name from the plan title or work description (e.g., `feat/crowd-sniff`). Present the rename as a recommended option alongside continuing as-is.
+
+   Then ask: "Continue working on `[current_branch]`, or create a new branch?"
+   - If continuing (with or without rename), proceed to step 3
    - If creating new, follow Option A or B below
 
    **If on the default branch**, choose how to proceed:
PATCH

echo "Gold patch applied."
