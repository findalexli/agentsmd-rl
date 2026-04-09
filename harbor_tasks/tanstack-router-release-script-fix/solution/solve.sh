#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/scripts/create-github-release.mjs b/scripts/create-github-release.mjs
index a4a37df444a..b9a1e0b0ab6 100644
--- a/scripts/create-github-release.mjs
+++ b/scripts/create-github-release.mjs
@@ -8,18 +8,26 @@ import { tmpdir } from 'node:os'
 const rootDir = path.join(import.meta.dirname, '..')
 const ghToken = process.env.GH_TOKEN || process.env.GITHUB_TOKEN

-// Get the previous release commit to diff against
-const lastReleaseHash = execSync(
-  'git log --oneline --grep="ci: changeset release" -n 1 --format=%H HEAD~1',
+// Get the previous release commit to diff against.
+// This script runs right after the "ci: changeset release" commit is pushed,
+// so HEAD is the release commit. We want commits between the previous release
+// and this one (exclusive of both release commits).
+const releaseLogs = execSync(
+  'git log --oneline --grep="ci: changeset release" --format=%H',
 )
   .toString()
   .trim()
+  .split('\n')
+  .filter(Boolean)

-const rangeFrom = lastReleaseHash || 'HEAD~1'
+// Current release commit is releaseLogs[0] (HEAD), previous is releaseLogs[1]
+const currentRelease = releaseLogs[0] || 'HEAD'
+const previousRelease = releaseLogs[1]
+const rangeFrom = previousRelease || `${currentRelease}~1`

-// Get commits since last release (include author email for username lookup)
+// Get commits between previous release and current release (exclude both)
 const rawLog = execSync(
-  `git log ${rangeFrom}..HEAD~1 --pretty=format:"%h %ae %s" --no-merges`,
+  `git log ${rangeFrom}..${currentRelease} --pretty=format:"%h %ae %s" --no-merges`,
 )
   .toString()
   .trim()
@@ -49,9 +57,10 @@ async function resolveUsername(email) {
   }
 }

-// Group commits by type
+// Group commits by conventional commit type
 const groups = {}
 for (const line of commits) {
+  // Format: "<hash> <email> <type>(<scope>): <subject>" or "<hash> <email> <type>: <subject>"
   const match = line.match(/^(\w+)\s+(\S+)\s+(\w+)(?:\(([^)]+)\))?:\s*(.+)$/)
   if (match) {
     const [, hash, email, type, scope, subject] = match
@@ -59,16 +68,13 @@ for (const line of commits) {
     if (!groups[key]) groups[key] = []
     groups[key].push({ hash, email, scope, subject })
   } else {
+    // Non-conventional commits (merge commits, etc.) go to Other
     if (!groups['Other']) groups['Other'] = []
-    const spaceIdx = line.indexOf(' ')
-    const rest = line.slice(spaceIdx + 1)
-    const spaceIdx2 = rest.indexOf(' ')
-    groups['Other'].push({
-      hash: line.slice(0, spaceIdx),
-      email: rest.slice(0, spaceIdx2),
-      scope: null,
-      subject: rest.slice(spaceIdx2 + 1),
-    })
+    const parts = line.split(' ')
+    const hash = parts[0]
+    const email = parts[1]
+    const subject = parts.slice(2).join(' ')
+    groups['Other'].push({ hash, email, scope: null, subject })
   }
 }

@@ -150,12 +156,13 @@ if (!tagExists) {
 }

 const prereleaseFlag = isPrerelease ? '--prerelease' : ''
+const latestFlag = isPrerelease ? '' : ' --latest'
 const tmpFile = path.join(tmpdir(), `release-notes-${tagName}.md`)
 fs.writeFileSync(tmpFile, body)

 try {
   execSync(
-    `gh release create ${tagName} ${prereleaseFlag} --title "Release ${titleDate}" --notes-file ${tmpFile} --latest`,
+    `gh release create ${tagName} ${prereleaseFlag} --title "Release ${titleDate}" --notes-file ${tmpFile}${latestFlag}`,
     { stdio: 'inherit' },
   )
   console.info(`GitHub release ${tagName} created.`)
PATCH

# Verify patch applied successfully
echo "Patch applied successfully"
