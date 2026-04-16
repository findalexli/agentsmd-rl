#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: skip if patch already applied
if grep -q "typeOrder = \[" scripts/create-github-release.mjs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/scripts/create-github-release.mjs b/scripts/create-github-release.mjs
index 4d62e1704bb..d7865bcfe0a 100644
--- a/scripts/create-github-release.mjs
+++ b/scripts/create-github-release.mjs
@@ -28,25 +28,6 @@ async function resolveUsername(email) {
   }
 }

-// Resolve author from a commit hash via git log
-const authorCache = {}
-async function resolveAuthorForCommit(hash) {
-  if (authorCache[hash] !== undefined) return authorCache[hash]
-
-  try {
-    const email = execSync(`git log -1 --format=%ae ${hash}`, {
-      encoding: 'utf-8',
-      stdio: ['pipe', 'pipe', 'ignore'],
-    }).trim()
-    const username = await resolveUsername(email)
-    authorCache[hash] = username
-    return username
-  } catch {
-    authorCache[hash] = null
-    return null
-  }
-}
-
 // Resolve author from a PR number via GitHub API
 const prAuthorCache = {}
 async function resolveAuthorForPR(prNumber) {
@@ -72,39 +53,6 @@ async function resolveAuthorForPR(prNumber) {
   }
 }

-// Append author info to changelog lines that contain PR refs or commit hashes
-async function appendAuthors(content) {
-  const lines = content.split('\n')
-  const result = []
-
-  for (const line of lines) {
-    if (!line.startsWith('- ')) {
-      result.push(line)
-      continue
-    }
-
-    // Try PR reference first: ([#6891](url))
-    const prMatch = line.match(/\[#(\d+)\]/)
-    if (prMatch) {
-      const username = await resolveAuthorForPR(prMatch[1])
-      result.push(username ? `${line} by @${username}` : line)
-      continue
-    }
-
-    // Fall back to commit hash: [`9a4d924`](url)
-    const commitMatch = line.match(/\[`([a-f0-9]{7,})`\]/)
-    if (commitMatch) {
-      const username = await resolveAuthorForCommit(commitMatch[1])
-      result.push(username ? `${line} by @${username}` : line)
-      continue
-    }
-
-    result.push(line)
-  }
-
-  return result.join('\n')
-}
-
 // Get the previous release commit to diff against.
 // This script runs right after the "ci: changeset release" commit is pushed,
 // so HEAD is the release commit.
@@ -167,37 +115,88 @@ for (const relPath of allPkgJsonPaths) {

 bumpedPackages.sort((a, b) => a.name.localeCompare(b.name))

-// Extract changelog entries from changeset-generated CHANGELOG.md files.
-// Changesets writes entries under "## <version>" headers. We extract the
-// content under the current version header for each bumped package.
+// Build changelog from git log between releases (conventional commits)
+const rangeFrom = previousRelease || `${currentRelease}~1`
+const rawLog = execSync(
+  `git log ${rangeFrom}..${currentRelease} --pretty=format:"%h %ae %s" --no-merges`,
+  { encoding: 'utf-8' },
+).trim()
+
+const typeOrder = [
+  'feat',
+  'fix',
+  'perf',
+  'refactor',
+  'docs',
+  'chore',
+  'test',
+  'ci',
+]
+const typeLabels = {
+  feat: 'Features',
+  fix: 'Fix',
+  perf: 'Performance',
+  refactor: 'Refactor',
+  docs: 'Documentation',
+  chore: 'Chore',
+  test: 'Tests',
+  ci: 'CI',
+}
+const typeIndex = (t) => {
+  const i = typeOrder.indexOf(t)
+  return i === -1 ? 99 : i
+}
+
+const groups = {}
+const commits = rawLog ? rawLog.split('\n') : []
+
+for (const line of commits) {
+  const match = line.match(/^(\w+)\s+(\S+)\s+(.*)$/)
+  if (!match) continue
+  const [, hash, email, subject] = match
+
+  // Skip release commits
+  if (subject.startsWith('ci: changeset release')) continue
+
+  // Parse conventional commit: type(scope): message
+  const conventionalMatch = subject.match(/^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/)
+  const type = conventionalMatch ? conventionalMatch[1] : 'other'
+  const scope = conventionalMatch ? conventionalMatch[2] || '' : ''
+  const message = conventionalMatch ? conventionalMatch[3] : subject
+
+  // Extract PR number if present
+  const prMatch = message.match(/\(#(\d+)\)/)
+  const prNumber = prMatch ? prMatch[1] : null
+
+  if (!groups[type]) groups[type] = []
+  groups[type].push({ hash, email, scope, message, prNumber })
+}
+
+// Build markdown grouped by conventional commit type
+const sortedTypes = Object.keys(groups).sort(
+  (a, b) => typeIndex(a) - typeIndex(b),
+)
+
 let changelogMd = ''
-for (const pkg of bumpedPackages) {
-  const changelogPath = path.join(packagesDir, pkg.dir, 'CHANGELOG.md')
-  if (!fs.existsSync(changelogPath)) continue
-
-  const changelog = fs.readFileSync(changelogPath, 'utf-8')
-
-  // Find the section for the current version: starts with "## <version>"
-  // and ends at the next "## " or end of file
-  const versionHeader = `## ${pkg.version}`
-  const startIdx = changelog.indexOf(versionHeader)
-  if (startIdx === -1) continue
-
-  const afterHeader = startIdx + versionHeader.length
-  const nextSection = changelog.indexOf('\n## ', afterHeader)
-  const section =
-    nextSection === -1
-      ? changelog.slice(afterHeader)
-      : changelog.slice(afterHeader, nextSection)
-
-  const content = section.trim()
-  if (content) {
-    const withAuthors = await appendAuthors(content)
-    changelogMd += `#### ${pkg.name}\n\n${withAuthors}\n\n`
+for (const type of sortedTypes) {
+  const label = typeLabels[type] || type.charAt(0).toUpperCase() + type.slice(1)
+  changelogMd += `### ${label}\n\n`
+
+  for (const commit of groups[type]) {
+    const scopePrefix = commit.scope ? `${commit.scope}: ` : ''
+    const cleanMessage = commit.message.replace(/\s*\(#\d+\)/, '')
+    const prRef = commit.prNumber ? ` (#${commit.prNumber})` : ''
+    const username = commit.prNumber
+      ? await resolveAuthorForPR(commit.prNumber)
+      : await resolveUsername(commit.email)
+    const authorSuffix = username ? ` by @${username}` : ''
+
+    changelogMd += `- ${scopePrefix}${cleanMessage}${prRef} (${commit.hash})${authorSuffix}\n`
   }
+  changelogMd += '\n'
 }

-if (!changelogMd) {
+if (!changelogMd.trim()) {
   changelogMd = '- No changelog entries\n\n'
 }
PATCH

echo "Gold patch applied successfully"
