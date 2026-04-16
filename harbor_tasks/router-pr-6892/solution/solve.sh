#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already applied
if grep -q "update-example-deps.mjs" package.json 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/package.json b/package.json
index 99d62684e6c..0650c4ff617 100644
--- a/package.json
+++ b/package.json
@@ -29,7 +29,7 @@
     "format": "prettier --experimental-cli --ignore-unknown '**/*' --write",
     "changeset": "changeset",
     "changeset:publish": "changeset publish",
-    "changeset:version": "changeset version && pnpm install --no-frozen-lockfile && pnpm format",
+    "changeset:version": "changeset version && node scripts/update-example-deps.mjs && pnpm install --no-frozen-lockfile && pnpm format",
     "gpt-generate": "node gpt/generate.js",
     "set-ts-version": "node scripts/set-ts-version.js",
     "labeler-generate": "node scripts/generate-labeler-config.ts",
diff --git a/scripts/update-example-deps.mjs b/scripts/update-example-deps.mjs
new file mode 100644
index 00000000000..87289a9e2a1
--- /dev/null
+++ b/scripts/update-example-deps.mjs
@@ -0,0 +1,49 @@
+import fs from 'fs'
+import path from 'node:path'
+import { globSync } from 'node:fs'
+
+const rootDir = path.join(import.meta.dirname, '..')
+
+// Build a map of package name -> current version from workspace
+const packagesDir = path.join(rootDir, 'packages')
+const packageMap = Object.fromEntries(
+  globSync('*/package.json', { cwd: packagesDir }).map((p) => {
+    const pkg = JSON.parse(fs.readFileSync(path.join(packagesDir, p), 'utf-8'))
+    return [pkg.name, pkg.version]
+  }),
+)
+
+// Update all example package.json files
+const examplesDir = path.join(rootDir, 'examples')
+const examplePkgPaths = globSync('**/package.json', {
+  cwd: examplesDir,
+  exclude: (p) => p.includes('node_modules'),
+})
+
+let updatedCount = 0
+
+for (const relPath of examplePkgPaths) {
+  const fullPath = path.join(examplesDir, relPath)
+  const content = fs.readFileSync(fullPath, 'utf-8')
+  const pkg = JSON.parse(content)
+
+  let changed = false
+  for (const depType of ['dependencies', 'devDependencies']) {
+    const deps = pkg[depType]
+    if (!deps) continue
+    for (const [name, range] of Object.entries(deps)) {
+      if (packageMap[name] && range !== `^${packageMap[name]}`) {
+        deps[name] = `^${packageMap[name]}`
+        changed = true
+      }
+    }
+  }
+
+  if (changed) {
+    fs.writeFileSync(fullPath, JSON.stringify(pkg, null, 2) + '\n')
+    updatedCount++
+    console.log(`Updated ${relPath}`)
+  }
+}
+
+console.log(`\nDone. Updated ${updatedCount} example(s).`)
PATCH

echo "Gold patch applied successfully."
