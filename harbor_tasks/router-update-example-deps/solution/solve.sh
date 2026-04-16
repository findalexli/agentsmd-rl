#!/bin/bash
set -e

REPO="/workspace/router"

cd "$REPO"

# Apply the gold patch
cat << 'PATCH' | git apply -
diff --git a/package.json b/package.json
index abc123..def456 100644
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
PATCH

# Create the update-example-deps.mjs script
mkdir -p "$REPO/scripts"

cat << 'SCRIPT' > "$REPO/scripts/update-example-deps.mjs"
import fs from 'fs'
import path from 'node:path'
import { globSync } from 'node:fs'

const rootDir = path.join(import.meta.dirname, '..')

// Build a map of package name -> current version from workspace
const packagesDir = path.join(rootDir, 'packages')
const packageMap = Object.fromEntries(
  globSync('*/package.json', { cwd: packagesDir }).map((p) => {
    const pkg = JSON.parse(fs.readFileSync(path.join(packagesDir, p), 'utf-8'))
    return [pkg.name, pkg.version]
  }),
)

// Update all example package.json files
const examplesDir = path.join(rootDir, 'examples')
const examplePkgPaths = globSync('**/package.json', {
  cwd: examplesDir,
  exclude: (p) => p.includes('node_modules'),
})

let updatedCount = 0

for (const relPath of examplePkgPaths) {
  const fullPath = path.join(examplesDir, relPath)
  const content = fs.readFileSync(fullPath, 'utf-8')
  const pkg = JSON.parse(content)

  let changed = false
  for (const depType of ['dependencies', 'devDependencies']) {
    const deps = pkg[depType]
    if (!deps) continue
    for (const [name, range] of Object.entries(deps)) {
      if (packageMap[name] && range !== `^${packageMap[name]}`) {
        deps[name] = `^${packageMap[name]}`
        changed = true
      }
    }
  }

  if (changed) {
    fs.writeFileSync(fullPath, JSON.stringify(pkg, null, 2) + '\n')
    updatedCount++
    console.log(`Updated ${relPath}`)
  }
}

console.log(`\\nDone. Updated ${updatedCount} example(s).`)
SCRIPT

echo "Solution applied successfully"
