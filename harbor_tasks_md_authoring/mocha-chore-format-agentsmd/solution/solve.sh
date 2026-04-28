#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mocha

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -96,6 +96,7 @@ For clean CI reproduction on a fresh checkout, prefer `npm ci --ignore-scripts`;
 Main workflow: `.github/workflows/mocha.yml`
 
 CI partitions checks into separate jobs:
+
 - `format:check`
 - `lint`
 - `test-smoke` (Node 20/22/24)
@@ -104,6 +105,7 @@ CI partitions checks into separate jobs:
 - `tsc`
 
 Reusable execution details in `.github/workflows/npm-script.yml`:
+
 - Uses `npm ci --ignore-scripts`
 - Default Node 22 unless overridden
 - `NODE_OPTIONS=--trace-warnings`
@@ -114,12 +116,14 @@ Reusable execution details in `.github/workflows/npm-script.yml`:
 During onboarding or after dependency refresh, you may encounter validation failures that reflect local environment or ecosystem drift rather than a persistent repository bug.
 
 Common patterns include:
+
 - Lint commands (for example, `npm run lint:code`) failing because new or stricter rules turn warnings into errors (such as via `--max-warnings 0`). Inspect the reported rule and location before changing lint configuration or adding suppressions.
 - Docs-related workflows where documentation generation succeeds but a subsequent static site or bundler step (for example, `astro build`) fails with runtime errors originating in third-party dependencies.
 
 Treat these as potential environment/version drift signals. Do not resolve them by broadly weakening checks (for example, relaxing lint strictness or skipping build steps) unless explicitly requested in the task.
 
 ## Change strategy for agents
+
 - Prefer smallest reproducible command to validate your specific edit first.
 - Add/adjust tests with behavior changes; do not change unrelated tests.
 - Avoid broad dependency upgrades unless task explicitly requests it.
PATCH

echo "Gold patch applied."
