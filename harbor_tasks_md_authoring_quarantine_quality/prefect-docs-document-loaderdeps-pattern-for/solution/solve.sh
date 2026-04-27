#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "`loaderDeps` controls which search params re-trigger the loader. When the loader" "ui-v2/src/routes/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/src/routes/AGENTS.md b/ui-v2/src/routes/AGENTS.md
@@ -50,6 +50,25 @@ export const Route = createFileRoute("/path")({
 });
 ```
 
+## loaderDeps and UI-Only Search Params
+
+`loaderDeps` controls which search params re-trigger the loader. When the loader re-runs, the route re-suspends and all local UI state resets (accordion sections collapse, dialogs close, etc.).
+
+Only include params that affect *what data* the loader fetches. Exclude params that only control UI state (pagination, active tab, open accordion):
+
+```ts
+loaderDeps: ({ search }) => {
+    // `page` and `flow` drive accordion pagination but don't affect
+    // loader fetches — exclude them to avoid re-suspending the route.
+    const { page, flow, ...rest } = search;
+    void page;
+    void flow;
+    return rest;
+},
+```
+
+Forgetting this causes every pagination click to re-run the loader, which collapses open accordions and other ephemeral UI state.
+
 ## Best Practices
 
 - Explicitly mark promises as ignored with the `void` operator when prefetching
PATCH

echo "Gold patch applied."
