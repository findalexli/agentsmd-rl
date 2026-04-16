#!/bin/bash
set -e

cd /workspace/router

# Check for idempotency - skip if already patched
if grep -q "isBreaking = conventionalMatch" scripts/create-github-release.mjs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/scripts/create-github-release.mjs b/scripts/create-github-release.mjs
index 9a8549e7666..d67fc52c21f 100644
--- a/scripts/create-github-release.mjs
+++ b/scripts/create-github-release.mjs
@@ -123,6 +123,7 @@ const rawLog = execSync(
 ).trim()

 const typeOrder = [
+  'breaking',
   'feat',
   'fix',
   'perf',
@@ -133,6 +134,7 @@ const typeOrder = [
   'ci',
 ]
 const typeLabels = {
+  breaking: '⚠️ Breaking Changes',
   feat: 'Features',
   fix: 'Fix',
   perf: 'Performance',
@@ -158,11 +160,12 @@ for (const line of commits) {
   // Skip release commits
   if (subject.startsWith('ci: changeset release')) continue

-  // Parse conventional commit: type(scope): message
-  const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/)
+  // Parse conventional commit: type(scope)!: message
+  const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?(!)?:\s*(.*)$/)
   const type = conventionalMatch ? conventionalMatch[1] : 'other'
+  const isBreaking = conventionalMatch ? !!conventionalMatch[3] : false
   const scope = conventionalMatch ? conventionalMatch[2] || '' : ''
-  const message = conventionalMatch ? conventionalMatch[3] : subject
+  const message = conventionalMatch ? conventionalMatch[4] : subject

   // Only include user-facing change types
   if (!['feat', 'fix', 'perf', 'refactor', 'build'].includes(type)) continue
@@ -171,8 +174,9 @@ for (const line of commits) {
   const prMatch = message.match(/\(#(\d+)\)/)
   const prNumber = prMatch ? prMatch[1] : null

-  if (!groups[type]) groups[type] = []
-  groups[type].push({ hash, email, scope, message, prNumber })
+  const bucket = isBreaking ? 'breaking' : type
+  if (!groups[bucket]) groups[bucket] = []
+  groups[bucket].push({ hash, email, scope, message, prNumber })
 }

 // Build markdown grouped by conventional commit type
PATCH

echo "Patch applied successfully"
