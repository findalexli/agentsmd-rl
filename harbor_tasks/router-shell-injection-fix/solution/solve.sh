#!/bin/bash
set -e

cd /workspace/router

# Apply the security fix: replace execSync with execFileSync for git show command
# This prevents shell injection when relPath contains shell metacharacters

cat > /tmp/fix.patch << 'PATCH'
--- a/scripts/create-github-release.mjs
+++ b/scripts/create-github-release.mjs
@@ -2,7 +2,7 @@
 import fs from 'fs'
 import path from 'node:path'
 import { globSync } from 'node:fs'
-import { execSync } from 'node:child_process'
+import { execSync, execFileSync } from 'node:child_process'
 import { tmpdir } from 'node:os'

 const rootDir = path.join(import.meta.dirname, '..')
@@ -80,8 +80,9 @@ for (const relPath of allPkgJsonPaths) {
   // Get the version from the previous release commit
   if (previousRelease) {
     try {
-      const prevContent = execSync(
-        `git show ${previousRelease}:packages/${relPath}`,
+      const prevContent = execFileSync(
+        'git',
+        ['show', `${previousRelease}:packages/${relPath}`],
         { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] },
       )
       const prevPkg = JSON.parse(prevContent)
PATCH

# Apply the patch
git apply /tmp/fix.patch

echo "Fix applied successfully"
