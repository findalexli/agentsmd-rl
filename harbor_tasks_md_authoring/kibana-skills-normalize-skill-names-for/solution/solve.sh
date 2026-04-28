#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kibana

# Idempotency guard
if grep -qF "name: ftr-testing" ".agent/skills/ftr-testing/SKILL.md" && grep -qF "name: scout-api-testing" ".agent/skills/scout-api-testing/SKILL.md" && grep -qF "name: scout-best-practices-reviewer" ".agent/skills/scout-best-practices-reviewer/SKILL.md" && grep -qF "name: scout-create-scaffold" ".agent/skills/scout-create-scaffold/SKILL.md" && grep -qF "name: scout-migrate-from-ftr" ".agent/skills/scout-migrate-from-ftr/SKILL.md" && grep -qF "name: scout-ui-testing" ".agent/skills/scout-ui-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/ftr-testing/SKILL.md b/.agent/skills/ftr-testing/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: FTR Testing
+name: ftr-testing
 description: Use when creating, updating, debugging, or reviewing Kibana Functional Test Runner (FTR) tests, including test structure, services/page objects, loadTestFile patterns, tags, and how to run FTR locally.
 ---
 
diff --git a/.agent/skills/scout-api-testing/SKILL.md b/.agent/skills/scout-api-testing/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Scout API Testing
+name: scout-api-testing
 description: Use when creating, updating, debugging, or reviewing Scout API tests in Kibana (apiTest/apiClient/requestAuth/samlAuth/apiServices), including auth choices, response assertions, and API service patterns.
 ---
 
diff --git a/.agent/skills/scout-best-practices-reviewer/SKILL.md b/.agent/skills/scout-best-practices-reviewer/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Scout Best Practices Reviewer
+name: scout-best-practices-reviewer
 description: Use when writing and reviewing Scout UI and API test files.
 ---
 
diff --git a/.agent/skills/scout-create-scaffold/SKILL.md b/.agent/skills/scout-create-scaffold/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Scout Create Scaffold
+name: scout-create-scaffold
 description: Generate or repair a Scout test scaffold for a Kibana plugin/package (test/scout*/{api,ui} Playwright configs, fixtures, example specs). Use when you need the initial Scout directory structure; prefer `node scripts/scout.js generate` with flags for non-interactive/LLM execution.
 ---
 
diff --git a/.agent/skills/scout-migrate-from-ftr/SKILL.md b/.agent/skills/scout-migrate-from-ftr/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Scout Migrate From FTR
+name: scout-migrate-from-ftr
 description: Use when migrating Kibana Functional Test Runner (FTR) tests to Scout, including decisions about UI vs API tests, mapping FTR services/page objects/hooks to Scout fixtures, and splitting loadTestFile patterns.
 ---
 
diff --git a/.agent/skills/scout-ui-testing/SKILL.md b/.agent/skills/scout-ui-testing/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Scout UI Testing
+name: scout-ui-testing
 description: Use when creating, updating, debugging, or reviewing Scout UI tests in Kibana (Playwright + Scout fixtures), including page objects, browser authentication, parallel UI tests (spaceTest/scoutSpace), a11y checks, and flake control.
 ---
 
PATCH

echo "Gold patch applied."
