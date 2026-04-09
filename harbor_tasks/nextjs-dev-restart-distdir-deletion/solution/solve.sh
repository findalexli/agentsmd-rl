#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q "wp.on('remove'" packages/next/src/server/lib/start-server.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/next/src/server/lib/start-server.ts b/packages/next/src/server/lib/start-server.ts
index eb60970010e874..3428ea536c1be6 100644
--- a/packages/next/src/server/lib/start-server.ts
+++ b/packages/next/src/server/lib/start-server.ts
@@ -524,25 +524,40 @@ export async function startServer(
     server.listen(port, hostname)
   })

+  // Watch config files for changes and distDir ancestors for deletion.
   if (isDev) {
-    function watchConfigFiles(
-      dirToWatch: string,
-      onChange: (filename: string) => void
-    ) {
-      const wp = new Watchpack()
-      wp.watch({
-        files: CONFIG_FILES.map((file) => path.join(dirToWatch, file)),
-      })
-      wp.on('change', onChange)
+    // Note: dir is absolute and normalized (`..` segments removed), `absDistDir`
+    // is also normalized because `path.join()` performs normalization. `distDir`
+    // does not have to be inside of `dir`!
+    const absDistDir = path.join(dir, distDir)
+    // always watch dir and absDistDir
+    const dirWatchPaths: string[] = [dir, absDistDir]
+    // also watch ancestors of absDistDir that are inside of dir.
+    let prevAncestor = absDistDir
+    while (true) {
+      const nextAncestor = path.dirname(prevAncestor)
+      // note: `dirname('/') === '/'` if we happen to reach the FS root
+      if (
+        !nextAncestor.startsWith(dir + path.sep) ||
+        nextAncestor === prevAncestor
+      ) {
+        break
       }
-    watchConfigFiles(dir, async (filename) => {
-      if (process.env.__NEXT_DISABLE_MEMORY_WATCHER) {
-        Log.info(
-          `Detected change, manual restart required due to '__NEXT_DISABLE_MEMORY_WATCHER' usage`
-        )
+      dirWatchPaths.push(nextAncestor)
+      prevAncestor = nextAncestor
+    }
+
+    const configFiles = CONFIG_FILES.map((file) => path.join(dir, file))
+
+    const wp = new Watchpack()
+    wp.watch({
+      files: configFiles,
+      missing: dirWatchPaths,
+    })
+    wp.on('change', async (filename) => {
+      if (!configFiles.includes(filename)) {
         return
       }
-
       Log.warn(
         `Found a change in ${path.basename(
           filename
@@ -550,6 +565,16 @@ export async function startServer(
       )
       process.exit(RESTART_EXIT_CODE)
     })
+    wp.on('remove', (removedPath: string) => {
+      if (dirWatchPaths.includes(removedPath)) {
+        Log.error(
+          `The directory at "${removedPath}" was deleted.\n\n` +
+            'Deleting this directory while Next.js is running can lead to ' +
+            'undefined behavior. Restarting the server to recover...'
+        )
+        process.exit(RESTART_EXIT_CODE)
+      }
+    })
   }

   return { distDir }

PATCH

echo "Patch applied successfully."
