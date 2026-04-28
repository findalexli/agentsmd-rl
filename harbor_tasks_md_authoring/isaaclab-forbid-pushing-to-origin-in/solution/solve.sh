#!/usr/bin/env bash
set -euo pipefail

cd /workspace/isaaclab

# Idempotency guard
if grep -qF "- **Never push to `origin` (`isaac-sim/IsaacLab`).** The `origin` remote is the " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -64,7 +64,7 @@ We use a wrapped python call within `./isaaclab.sh`.
 
 ### Pre-commit (lint/format hooks)
 
-**CRITICAL: Always run pre-commit hooks BEFORE committing, not after.**
+**CRITICAL: Always run pre-commit hooks BEFORE committing and BEFORE pushing.**
 
 Proper workflow:
 1. Make your code changes
@@ -73,15 +73,17 @@ Proper workflow:
 4. Stage the modified files with `git add`
 5. Run `./isaaclab.sh -f` again to ensure all checks pass
 6. Only then create your commit with `git commit`
+7. Verify pre-commit still passes before pushing — never push commits that haven't been checked
 
 ```bash
 # Run pre-commit checks on all files
 ./isaaclab.sh -f
 ```
 
-**Common mistake to avoid:**
+**Common mistakes to avoid:**
 - Don't commit first and then run pre-commit (requires amending commits)
-- Do run pre-commit before committing (clean workflow)
+- Don't push before running pre-commit (pushes broken code to the remote)
+- Do run pre-commit before committing and before pushing (clean workflow)
 
 **When reviewing code** (e.g. via a code-reviewer agent), always run `./isaaclab.sh -f` as part of the review to catch formatting or lint issues early.
 
@@ -152,6 +154,7 @@ Follow conventional commit message practices.
 ## Sandbox & Networking
 
 - Network access (e.g., `git push`) is blocked by the sandbox. Use `dangerouslyDisableSandbox: true` so the user gets an approval prompt — don't ask them to run it manually.
+- **Never push to `origin` (`isaac-sim/IsaacLab`).** The `origin` remote is the public upstream repository. Push to your own fork remote (e.g., `antoine`, `alex`) or to the remote of the PR you are working on. If the correct remote is unclear, ask the user before pushing.
 
 ## GitHub Actions and CI/CD
 
PATCH

echo "Gold patch applied."
