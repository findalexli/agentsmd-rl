#!/usr/bin/env bash
set -euo pipefail

cd /workspace/everything-claude-code

# Idempotency guard
if grep -qF "- Before treating a checkpoint as satisfied, verify that the commit is reachable" "skills/tdd-workflow/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/tdd-workflow/SKILL.md b/skills/tdd-workflow/SKILL.md
@@ -47,6 +47,19 @@ ALWAYS write tests first, then implement code to make tests pass.
 - Browser automation
 - UI interactions
 
+### 4. Git Checkpoints
+- If the repository is under Git, create a checkpoint commit after each TDD stage
+- Do not squash or rewrite these checkpoint commits until the workflow is complete
+- Each checkpoint commit message must describe the stage and the exact evidence captured
+- Count only commits created on the current active branch for the current task
+- Do not treat commits from other branches, earlier unrelated work, or distant branch history as valid checkpoint evidence
+- Before treating a checkpoint as satisfied, verify that the commit is reachable from the current `HEAD` on the active branch and belongs to the current task sequence
+- The preferred compact workflow is:
+  - one commit for failing test added and RED validated
+  - one commit for minimal fix applied and GREEN validated
+  - one optional commit for refactor complete
+- Separate evidence-only commits are not required if the test commit clearly corresponds to RED and the fix commit clearly corresponds to GREEN
+
 ## TDD Workflow Steps
 
 ### Step 1: Write User Journeys
@@ -87,6 +100,29 @@ npm test
 # Tests should fail - we haven't implemented yet
 ```
 
+This step is mandatory and is the RED gate for all production changes.
+
+Before modifying business logic or other production code, you must verify a valid RED state via one of these paths:
+- Runtime RED:
+  - The relevant test target compiles successfully
+  - The new or changed test is actually executed
+  - The result is RED
+- Compile-time RED:
+  - The new test newly instantiates, references, or exercises the buggy code path
+  - The compile failure is itself the intended RED signal
+- In either case, the failure is caused by the intended business-logic bug, undefined behavior, or missing implementation
+- The failure is not caused only by unrelated syntax errors, broken test setup, missing dependencies, or unrelated regressions
+
+A test that was only written but not compiled and executed does not count as RED.
+
+Do not edit production code until this RED state is confirmed.
+
+If the repository is under Git, create a checkpoint commit immediately after this stage is validated.
+Recommended commit message format:
+- `test: add reproducer for <feature or bug>`
+- This commit may also serve as the RED validation checkpoint if the reproducer was compiled and executed and failed for the intended reason
+- Verify that this checkpoint commit is on the current active branch before continuing
+
 ### Step 4: Implement Code
 Write minimal code to make tests pass:
 
@@ -97,19 +133,36 @@ export async function searchMarkets(query: string) {
 }
 ```
 
+If the repository is under Git, stage the minimal fix now but defer the checkpoint commit until GREEN is validated in Step 5.
+
 ### Step 5: Run Tests Again
 ```bash
 npm test
 # Tests should now pass
 ```
 
+Rerun the same relevant test target after the fix and confirm the previously failing test is now GREEN.
+
+Only after a valid GREEN result may you proceed to refactor.
+
+If the repository is under Git, create a checkpoint commit immediately after GREEN is validated.
+Recommended commit message format:
+- `fix: <feature or bug>`
+- The fix commit may also serve as the GREEN validation checkpoint if the same relevant test target was rerun and passed
+- Verify that this checkpoint commit is on the current active branch before continuing
+
 ### Step 6: Refactor
 Improve code quality while keeping tests green:
 - Remove duplication
 - Improve naming
 - Optimize performance
 - Enhance readability
 
+If the repository is under Git, create a checkpoint commit immediately after refactoring is complete and tests remain green.
+Recommended commit message format:
+- `refactor: clean up after <feature or bug> implementation`
+- Verify that this checkpoint commit is on the current active branch before considering the TDD cycle complete
+
 ### Step 7: Verify Coverage
 ```bash
 npm run test:coverage
PATCH

echo "Gold patch applied."
