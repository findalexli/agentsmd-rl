#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-copilot-for-azure

# Idempotency guard
if grep -qF "description: \"Investigate a failing integration test from a GitHub issue. Downlo" ".github/skills/investigate-integration-test/SKILL.md" && grep -qF "description: \"Submit a pull request with skill fixes. Validates skill structure," ".github/skills/submit-skill-fix-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/investigate-integration-test/SKILL.md b/.github/skills/investigate-integration-test/SKILL.md
@@ -0,0 +1,26 @@
+---
+name: investigate-integration-test
+description: "Investigate a failing integration test from a GitHub issue. Downloads logs/artifacts, analyzes the failure, examines relevant skills, and suggests fixes. TRIGGERS: investigate integration test, debug integration test, failing integration test, test failure investigation, diagnose test failure, analyze test issue"
+license: MIT
+metadata:
+  author: Microsoft
+  version: "1.0.0"
+---
+
+# Integration Test Investigation
+
+Investigates a failing integration test given a GitHub issue in `microsoft/GitHub-Copilot-for-Azure`.
+
+## When to Use This Skill
+
+- A GitHub issue links to a failing integration test run
+- You need to diagnose why an integration test is failing
+- You want to understand a test failure before implementing a fix
+
+## Steps
+
+1. Read the GitHub issue.
+2. Download the test logs and artifacts from the linked run.
+3. Look through the logs/artifacts and analyze the test with the prompt specified in the issue to diagnose the failure.
+4. Examine the relevant skills under `plugin/skills` for context.
+5. Offer a suggested fix for each identified problem. Do not implement any fixes without the user's approval.
diff --git a/.github/skills/submit-skill-fix-pr/SKILL.md b/.github/skills/submit-skill-fix-pr/SKILL.md
@@ -0,0 +1,28 @@
+---
+name: submit-skill-fix-pr
+description: "Submit a pull request with skill fixes. Validates skill structure, bumps versions, and creates a PR with a proper description. TRIGGERS: submit skill fix, create fix PR, skill fix pull request, submit PR, push skill fix"
+license: MIT
+metadata:
+  author: Microsoft
+  version: "1.0.0"
+---
+
+# Submit Skill Fix PR
+
+Creates a pull request after committing skill fixes in `microsoft/GitHub-Copilot-for-Azure`.
+
+## When to Use This Skill
+
+- You have committed skill fixes and need to submit a PR
+- You need to validate skill structure before pushing
+- You want to create a properly formatted fix PR
+
+## Steps
+
+1. Install NPM dependencies in the `scripts` directory, if necessary.
+2. From the `scripts` directory run `npm run frontmatter` and `npm run references` to validate the skill structure. Fix and commit any problems.
+3. Ensure that skill version has been bumped for any updated SKILL.md.
+4. Push the branch to origin and create a PR into upstream. The PR description should include:
+   1. A brief description of the problem(s).
+   2. A brief description of the fix(es) and how they address the problems.
+   3. A "Fixes #<issue_number>" note. Ask the user if you don't know the issue number.
PATCH

echo "Gold patch applied."
