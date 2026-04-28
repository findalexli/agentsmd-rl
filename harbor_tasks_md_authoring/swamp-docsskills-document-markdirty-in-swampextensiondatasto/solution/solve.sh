#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swamp

# Idempotency guard
if grep -qF "watermark to short-circuit zero-diff syncs (the recommended fast-path pattern \u2014" ".claude/skills/swamp-extension-datastore/references/api.md" && grep -qF "// pushChanged walks the cache unconditionally, there's nothing" ".claude/skills/swamp-extension-datastore/references/examples.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/swamp-extension-datastore/references/api.md b/.claude/skills/swamp-extension-datastore/references/api.md
@@ -165,6 +165,7 @@ Optional interface for remote datastore synchronization.
 interface DatastoreSyncService {
   pullChanged(): Promise<void>;
   pushChanged(): Promise<void>;
+  markDirty(): Promise<void>;
 }
 ```
 
@@ -177,3 +178,19 @@ read/write operations on remote datastores.
 
 Push changed files from the local cache to the remote datastore. Called after
 write operations complete.
+
+### `markDirty()`
+
+Signal that the local cache has uncommitted work. Swamp core calls this at the
+start of every repository-layer mutation that writes into the cache (e.g.
+`save`, `delete`, `rename`), **before** the write begins — a crash mid-write
+still leaves the watermark dirty.
+
+The method only matters for implementations that maintain a clean/dirty
+watermark to short-circuit zero-diff syncs (the recommended fast-path pattern —
+see `design/datastores.md`). Those implementations MUST flip the watermark to
+dirty here so the next `pushChanged` cannot skip past core's writes.
+Implementations that unconditionally walk the cache on every `pushChanged` have
+nothing to invalidate and can return `Promise.resolve()`.
+
+`markDirty()` must be idempotent and cheap — core does not deduplicate calls.
diff --git a/.claude/skills/swamp-extension-datastore/references/examples.md b/.claude/skills/swamp-extension-datastore/references/examples.md
@@ -245,6 +245,13 @@ export const datastore = {
           // Upload changed files from cachePath to remote
           console.log(`Pushing from ${cachePath} to ${parsed.endpoint}`);
         },
+        markDirty: () => {
+          // Swamp core calls this before every cache write. If your
+          // pushChanged walks the cache unconditionally, there's nothing
+          // to invalidate — no-op. If you add a clean/dirty sidecar
+          // (fast-path pattern in design/datastores.md), flip it here.
+          return Promise.resolve();
+        },
       }),
 
       resolveDatastorePath: (repoDir: string) => {
PATCH

echo "Gold patch applied."
