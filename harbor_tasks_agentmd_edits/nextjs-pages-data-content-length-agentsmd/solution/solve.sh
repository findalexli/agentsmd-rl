#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'pnpm new-test -- --args' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 64d3c177bdabb2..70970ba85ab5ac 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -148,13 +148,13 @@ pnpm test-dev-turbo test/development/
 Generating tests using `pnpm new-test` is mandatory.

 ```bash
-# Use --args for non-interactive mode
-# Format: pnpm new-test --args <appDir> <name> <type>
+# Use --args for non-interactive mode (forward args to the script using `--`)
+# Format: pnpm new-test -- --args <appDir> <name> <type>
 # appDir: true/false (is this for app directory?)
 # name: test name (e.g. "my-feature")
 # type: e2e | production | development | unit

-pnpm new-test --args true my-feature e2e
+pnpm new-test -- --args true my-feature e2e
 ```

 **Analyzing test output efficiently:**
@@ -400,7 +400,7 @@ Core runtime/bundling rules (always apply; skills above expand on these with ver
 ### Test Gotchas

 - **Cache components enables PPR by default**: When `__NEXT_CACHE_COMPONENTS=true`, most app-dir pages use PPR implicitly. Dedicated `ppr-full/` and `ppr/` test suites are mostly `describe.skip` (migrating to cache components). To test PPR codepaths, run normal app-dir e2e tests with `__NEXT_CACHE_COMPONENTS=true` rather than looking for explicit PPR test suites.
-- **Quick smoke testing with toy apps**: For fast feedback, generate a minimal test fixture with `pnpm new-test --args true <name> e2e`, then run the dev server directly with `node packages/next/dist/bin/next dev --port <port>` and `curl --max-time 10`. This avoids the overhead of the full test harness and gives immediate feedback on hangs/crashes.
+  -- **Quick smoke testing with toy apps**: For fast feedback, generate a minimal test fixture with `pnpm new-test -- --args true <name> e2e`, then run the dev server directly with `node packages/next/dist/bin/next dev --port <port>` and `curl --max-time 10`. This avoids the overhead of the full test harness and gives immediate feedback on hangs/crashes.
 - Mode-specific tests need `skipStart: true` + manual `next.start()` in `beforeAll` after mode check
 - Don't rely on exact log messages - filter by content patterns, find sequences not positions
 - **Snapshot tests vary by env flags**: Tests with inline snapshots can produce different output depending on env flags. When updating snapshots, always run the test with the exact env flags the CI job uses (check `.github/workflows/build_and_test.yml` `afterBuild:` sections). Turbopack resolves `react-dom/server.edge` (no Node APIs like `renderToPipeableStream`), while webpack resolves the `.node` build (has them).
diff --git a/packages/next/src/server/route-modules/pages/pages-handler.ts b/packages/next/src/server/route-modules/pages/pages-handler.ts
index c4d5f36e4b6412..4534c1d7978bbf 100644
--- a/packages/next/src/server/route-modules/pages/pages-handler.ts
+++ b/packages/next/src/server/route-modules/pages/pages-handler.ts
@@ -526,16 +526,13 @@ export const getHandler = ({
             return {
               value: {
                 kind: CachedRouteKind.PAGES,
-                html: new RenderResult(
-                  Buffer.from(previousCacheEntry.value.html),
-                  {
-                    contentType: HTML_CONTENT_TYPE_HEADER,
-                    metadata: {
-                      statusCode: previousCacheEntry.value.status,
-                      headers: previousCacheEntry.value.headers,
-                    },
-                  }
-                ),
+                html: new RenderResult(previousCacheEntry.value.html, {
+                  contentType: HTML_CONTENT_TYPE_HEADER,
+                  metadata: {
+                    statusCode: previousCacheEntry.value.status,
+                    headers: previousCacheEntry.value.headers,
+                  },
+                }),
                 pageData: {},
                 status: previousCacheEntry.value.status,
                 headers: previousCacheEntry.value.headers,
@@ -740,13 +737,10 @@ export const getHandler = ({
           // anymore
           result:
             isNextDataRequest && !isErrorPage && !is500Page
-              ? new RenderResult(
-                  Buffer.from(JSON.stringify(result.value.pageData)),
-                  {
-                    contentType: JSON_CONTENT_TYPE_HEADER,
-                    metadata: result.value.html.metadata,
-                  }
-                )
+              ? new RenderResult(JSON.stringify(result.value.pageData), {
+                  contentType: JSON_CONTENT_TYPE_HEADER,
+                  metadata: result.value.html.metadata,
+                })
               : result.value.html,
           generateEtags: nextConfig.generateEtags,
           poweredByHeader: nextConfig.poweredByHeader,

PATCH

echo "Patch applied successfully."
