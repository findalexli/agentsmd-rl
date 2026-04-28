#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency check
if grep -q "getBenchName(): string" packages/route-pattern/bench/href.bench.ts; then
  echo "Fix already applied, exiting."
  exit 0
fi

# Apply the fix
git apply <<'PATCH'
diff --git a/packages/route-pattern/bench/href.bench.ts b/packages/route-pattern/bench/href.bench.ts
index 21e5d7e00b2..983eb69cf0e 100644
--- a/packages/route-pattern/bench/href.bench.ts
+++ b/packages/route-pattern/bench/href.bench.ts
@@ -7,10 +7,25 @@
  * Therefore, all `bench` calls happen in their own `describe` block, and the name passed to `bench` is arbitrary.
  */

+import { execSync } from 'node:child_process'
 import { bench, describe } from 'vitest'
 import { RoutePattern } from '@remix-run/route-pattern'

-let benchName = 'bench'
+let benchName = getBenchName()
+
+/**
+ * Returns the benchmark name as `<branch> (<short commit>)`.
+ * Fallback to 'bench' if git commands fail.
+ */
+function getBenchName(): string {
+  try {
+    let branch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim()
+    let shortCommit = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim()
+    return `${branch} (${shortCommit})`
+  } catch {
+    return 'bench'
+  }
+}

 describe('static', () => {
   let pattern = new RoutePattern('/posts/new')
PATCH
