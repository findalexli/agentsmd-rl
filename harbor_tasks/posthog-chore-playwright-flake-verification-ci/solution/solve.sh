#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'verify-playwright-new-tests-and-snapshots' .github/scripts/verify-playwright-new-tests-and-snapshots.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.agents/skills/playwright-test/SKILL.md b/.agents/skills/playwright-test/SKILL.md
index f62b5db72883..43630f73a722 100644
--- a/.agents/skills/playwright-test/SKILL.md
+++ b/.agents/skills/playwright-test/SKILL.md
@@ -4,13 +4,13 @@ description: Write a playwright test, make sure it runs, and is not flaky.
 allowed-tools: Bash, Read, Edit, Write, Glob, Grep, Agent, mcp__playwright__*
 ---

+Read @playwright/README.md for best practices, gotchas, and how to run tests.
+
 ## Rules

-- Don't use any locators with css selectors, prefer getting elements via accessibility roles or data-testids, add data-attr if required.
-- Write fewer longer tests that do multiple things, split up by test.steps into logical steps
-- Use page object models for common tasks and accessing common elements
+- Follow the best practices in the README strictly
 - After UI interactions, always assert on UI changes, do not assert on network requests resolving
-- Never put an if statement in a test
+- **Keep looping until all tests pass.** Do not give up or ask the user for help. You must resolve every failure yourself.

 ## Instructions

@@ -27,7 +27,6 @@ After your exploration, present the plan to me for confirmation or any changes.
 - Write the tests, making sure to use common patterns used in neighbouring files.
 - Run the tests with `BASE_URL='http://localhost:8010' pnpm --filter=@posthog/playwright exec playwright test <file name> --retries 0 --workers 3`
 - Debug any failures. Look at screen shots, if needed launch the playwright mcp skills to interact with the browser. Go back to step 1 after attempting a fix.
-- **Keep looping until all tests pass.** Do not give up or ask the user for help. You must resolve every failure yourself.

 ### Step 3: Ensure no flaky tests

diff --git a/.github/scripts/verify-playwright-new-tests-and-snapshots.sh b/.github/scripts/verify-playwright-new-tests-and-snapshots.sh
new file mode 100755
index 000000000000..ae81f74a9004
--- /dev/null
+++ b/.github/scripts/verify-playwright-new-tests-and-snapshots.sh
@@ -0,0 +1,91 @@
+#!/bin/bash
+set -euo pipefail
+
+# Verify changed Playwright test files are stable by re-running them with --repeat-each.
+# Catches flaky tests before they land — covers new files, unskipped tests, and any other modifications.
+#
+# Usage:
+#   verify-playwright-new-tests-and-snapshots.sh <base_sha> [repeat_count]
+#
+# Example:
+#   .github/scripts/verify-playwright-new-tests-and-snapshots.sh origin/master 10
+
+if [ $# -lt 1 ] || [ $# -gt 2 ]; then
+    echo "Usage: $0 <base_sha> [repeat_count]" >&2
+    exit 1
+fi
+
+BASE_SHA="$1"
+REPEAT_COUNT="${2:-10}"
+
+if ! [[ "$REPEAT_COUNT" =~ ^[0-9]+$ ]] || [ "$REPEAT_COUNT" -lt 1 ]; then
+    echo "Error: repeat_count must be a positive integer" >&2
+    exit 1
+fi
+
+echo "Detecting changed Playwright test files since $BASE_SHA..."
+
+# Clean up stale results from a previous run (depot runners reuse workspaces).
+RESULTS_FILE="playwright/flake-verification-results.json"
+rm -f "$RESULTS_FILE"
+
+# All spec files touched by the PR (added or modified).
+changed_test_files=$(git diff --name-only "$BASE_SHA..HEAD" -- 'playwright/**/*.spec.ts')
+
+if [ -z "$changed_test_files" ]; then
+    echo "No changed Playwright test files found — skipping flake verification"
+    exit 0
+fi
+declare -a tests_to_run=()
+while IFS= read -r test_file; do
+    if [ ! -f "$test_file" ]; then
+        echo "Warning: $test_file no longer exists (deleted in PR) — skipping"
+        continue
+    fi
+
+    # Strip the playwright/ prefix — Playwright runs relative to its project root.
+    tests_to_run+=("${test_file#playwright/}")
+done <<< "$changed_test_files"
+
+if [ ${#tests_to_run[@]} -eq 0 ]; then
+    echo "No runnable Playwright test files to verify"
+    exit 0
+fi
+
+echo "Verifying ${#tests_to_run[@]} file(s) with --repeat-each=$REPEAT_COUNT:"
+printf "  %s\n" "${tests_to_run[@]}"
+
+# Write a JSON results file for the PR comment step to pick up.
+write_results() {
+    local status="$1"
+    local message="$2"
+    local files_json
+    files_json=$(printf '%s\n' "${tests_to_run[@]}" | jq -R . | jq -s .)
+    jq -n \
+        --arg status "$status" \
+        --arg message "$message" \
+        --argjson files "$files_json" \
+        --argjson repeat "$REPEAT_COUNT" \
+        '{status: $status, message: $message, files: $files, repeat_count: $repeat}' \
+        > "$RESULTS_FILE"
+}
+
+set +e
+# No --reporter override — uses playwright.config.ts reporters (html + json in CI).
+# This overwrites the main run's report, which is fine: if verification fails,
+# the verification report is the one that matters (the main tests passed).
+pnpm --filter=@posthog/playwright exec playwright test "${tests_to_run[@]}" \
+    --workers=1 --repeat-each="$REPEAT_COUNT" --retries=0
+test_exit=$?
+set -e
+
+if [ "$test_exit" -ne 0 ]; then
+    echo ""
+    echo "Flake verification failed — one or more changed test files are unstable"
+    write_results "failed" "Flake verification failed — changed tests are unstable across $REPEAT_COUNT repetitions"
+    exit 1
+fi
+
+echo ""
+echo "Flake verification passed — all changed test files stable across $REPEAT_COUNT repetitions"
+write_results "passed" "All changed test files stable across $REPEAT_COUNT repetitions"
diff --git a/.github/workflows/ci-e2e-playwright.yml b/.github/workflows/ci-e2e-playwright.yml
index 26aef63a573a..9a9014884f65 100644
--- a/.github/workflows/ci-e2e-playwright.yml
+++ b/.github/workflows/ci-e2e-playwright.yml
@@ -458,6 +458,14 @@ jobs:
                     fi
                   fi

+            - name: Verify changed Playwright tests are stable
+              if: success() && github.event_name == 'pull_request'
+              shell: bash
+              run: |
+                  BASE_SHA="${{ github.event.pull_request.base.sha }}"
+                  git fetch --no-tags --prune --depth=50 origin "$BASE_SHA"
+                  .github/scripts/verify-playwright-new-tests-and-snapshots.sh "$BASE_SHA" 10
+
             # Create git patch for aggregation (handles A/M/D including binary files)
             # Only run in UPDATE mode - CHECK mode doesn't update snapshots
             # Run even if tests failed, as long as snapshots may have been updated
@@ -610,6 +618,16 @@ jobs:
                           }
                       } catch {}

+                      // Flake verification results for changed test files
+                      try {
+                          const flakeResults = JSON.parse(fs.readFileSync('playwright/flake-verification-results.json', 'utf8'));
+                          if (flakeResults.status === 'failed') {
+                              const fileList = flakeResults.files.map(f => `- \`${f}\``).join('\n');
+                              const flakeReportLink = reportUrl ? ` [View report →](${reportUrl})` : '';
+                              extraLines += `\n\n🔁 **Flake verification failed** (--repeat-each=${flakeResults.repeat_count}):\n${fileList}\n\nThe report only shows the tests under verification.${flakeReportLink} Fix these before merging.`;
+                          }
+                      } catch {}
+
                       const { data: comments } = await github.rest.issues.listComments({
                           owner: context.repo.owner,
                           repo: context.repo.repo,
@@ -633,7 +651,7 @@ jobs:
                       const reportLink = reportUrl ? ` · [View test results →](${reportUrl})` : '';
                       const snapshotMode = '${{ needs.detect-snapshot-mode.outputs.mode }}';
                       const snapshotHint = (snapshotMode === 'check' && failed.length > 0)
-                          ? '\n\n---\n**If your changes intentionally update screenshots:** add the `update-snapshots` label, then push an empty commit or merge master to trigger a new run. Screenshots will be auto-committed.\n**If you didn\'t change any UI:** this is likely a flaky screenshot — wait for a fix to land on master.'
+                          ? '\n\n**If your changes intentionally update screenshots:** add the `update-snapshots` label, then push an empty commit or merge master to trigger a new run. Screenshots will be auto-committed.\n**If you didn\'t change any UI:** this is likely a flaky screenshot — wait for a fix to land on master.'
                           : '';
                       const footer = '\n\n\n*These issues are not necessarily caused by your changes.*\n*Annoyed by this comment? Help fix flakies and failures and it\'ll disappear!*';
                       const body = `${marker}\n🎭 Playwright report${reportLink}${extraLines}${snapshotHint}${footer}`;
diff --git a/playwright/README.md b/playwright/README.md
index 3f4d51203b2f..e253b3ee5031 100644
--- a/playwright/README.md
+++ b/playwright/README.md
@@ -26,13 +26,22 @@ It will explore the UI with Playwright MCP tools, plan the tests, implement them

 ## Writing tests

-### Flaky tests are almost always due to not waiting for the right thing
+### Best practices

-Consider adding a better selector, an intermediate step like waiting for URL or page title to change, or waiting for a critical network request to complete.
+- Don't use CSS selectors — prefer accessibility roles (`getByRole`) or `getByTestId()` which maps to `data-attr` in our config. Add `data-attr` to components if needed.
+- Write fewer, longer tests that do multiple things. Split logical steps with `test.step()`.
+- Use page object models for common tasks and accessing common elements (see `page-models/`).
+- After UI interactions, assert on UI changes — don't assert on network requests resolving.
+- Never put conditional logic (`if`) in a test.

-### Useful output from Playwright
+### Gotchas

-If you write a selector that is too loose and matches multiple elements, Playwright will output all the matches. With a better selector for each:
+**Flaky tests are almost always due to not waiting for the right thing.**
+Consider adding a better selector, an intermediate step like waiting for URL or page title to change,
+or waiting for a critical network request to complete.
+
+**Loose selectors cause strict mode violations.**
+If a selector matches multiple elements, Playwright will show all matches — use the output to narrow down:

 ```text
 Error: locator.click: Error: strict mode violation: locator('text=Set a billing limit') resolved to 2 elements:

PATCH

echo "Patch applied successfully."
