#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ag-charts

# Idempotency guard
if grep -qF "-   **Test real implementations, not helpers**: Avoid creating test helper funct" "tools/prompts/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tools/prompts/AGENTS.md b/tools/prompts/AGENTS.md
@@ -11,6 +11,7 @@ This file provides guidance to AI Agents when working with code in this reposito
 -   **Typechecking:** Run `nx build:types <package>` from the repo root before proposing commits.
 -   **Linting:** Run `nx lint <package>` from the repo root before proposing commits.
 -   **Baseline verification:** Expect to run `nx test ag-charts-community`, `nx test ag-charts-enterprise`, and `nx e2e ag-charts-website` after meaningful chart changes.
+-   **Test verification patterns:** When writing or modifying tests, review similar tests to ensure consistent verification patterns (e.g., if similar tests verify domains, your tests should too).
 -   **Context docs:** Skim `tools/prompts/technology-stack.md` for stack or architectural decisions before introducing new patterns.
 
 ## Project Overview
@@ -90,6 +91,19 @@ Core dependency chain: `ag-charts-core` → `ag-charts-types` → `ag-charts-loc
 -   **Benchmarks**: Performance regression testing with memory profiling
 -   **Visual regression**: Canvas rendering snapshot comparisons
 
+### Testing Best Practices
+
+-   **Test real implementations, not helpers**: Avoid creating test helper functions that duplicate production logic. Instead, test the actual implementation through its public API (e.g., using `DataSet` to test data operations rather than a helper function that reimplements the logic).
+-   **Look for existing patterns first**: Before writing new tests, review similar existing tests to maintain consistency in:
+    -   Verification patterns (e.g., if similar tests verify domains, yours should too)
+    -   Test structure and organization
+    -   Assertion styles and completeness
+-   **Test completeness checklist**:
+    -   Do similar tests verify more properties that this one should also verify?
+    -   Are all important outputs verified (data, keys, columns, domains, metadata, etc.)?
+    -   Does this test exercise the real code path users will hit?
+-   **Naming clarity**: Variable and parameter names should clearly convey intent, especially for boolean flags (e.g., `columnNeedValueOf` is clearer than `columnValueTypes` for a boolean array).
+
 ### Code Quality
 
 -   **ESLint**: Comprehensive setup with TypeScript rules, SonarJS, and custom AG Charts rules
@@ -164,6 +178,11 @@ Core dependency chain: `ag-charts-core` → `ag-charts-types` → `ag-charts-loc
 
 -   Make sure to run `nx format` on any changes to ensure consistent formatting before commit.
 -   Prefer running `nx format` in the root of the repo to format changes, as there are config nuances that aren't taken into account when directly running tooling in more specific places.
+-   **Self-review before committing**:
+    -   Read through your changes as if you were the reviewer
+    -   Check for consistency with similar existing code patterns
+    -   For test changes, verify completeness by comparing with related tests in the same file
+    -   Ensure naming clearly conveys intent (especially for boolean/flag variables)
 
 ### Code Quality Guidelines
 
@@ -195,6 +214,10 @@ Core dependency chain: `ag-charts-core` → `ag-charts-types` → `ag-charts-loc
 ## Code Review Guidelines
 
 -   When reviewing a PR, don't comment on lines not changed in the PR itself; we have tech-debt but can't fix it all at once.
+-   **For test changes**:
+    -   Ensure tests exercise real implementations, not test-only helper functions
+    -   Verify consistency: if similar tests check X, all related tests should check X
+    -   Look for opportunities to improve test coverage without adding redundancy
 -   See `tools/prompts/pr-review.md` for detailed PR review instructions.
 
 ## JIRA Ticket Search Guidelines
PATCH

echo "Gold patch applied."
