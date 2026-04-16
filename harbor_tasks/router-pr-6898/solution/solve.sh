#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already applied
if grep -q "resolveAuthorForPR" scripts/create-github-release.mjs; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch using git apply for better compatibility
git apply --verbose <<'PATCH'
diff --git a/scripts/create-github-release.mjs b/scripts/create-github-release.mjs
index 0c6a90cf6e5..4d62e1704bb 100644
--- a/scripts/create-github-release.mjs
+++ b/scripts/create-github-release.mjs
@@ -28,7 +28,7 @@ async function resolveUsername(email) {
   }
 }

-// Resolve a commit hash to a "by @username" string
+// Resolve author from a commit hash via git log
 const authorCache = {}
 async function resolveAuthorForCommit(hash) {
   if (authorCache[hash] !== undefined) return authorCache[hash]
@@ -39,29 +39,67 @@ async function resolveAuthorForCommit(hash) {
       stdio: ['pipe', 'pipe', 'ignore'],
     }).trim()
     const username = await resolveUsername(email)
-    const result = username ? ` by @${username}` : ''
-    authorCache[hash] = result
-    return result
+    authorCache[hash] = username
+    return username
   } catch {
-    authorCache[hash] = ''
-    return ''
+    authorCache[hash] = null
+    return null
+  }
+}
+
+// Resolve author from a PR number via GitHub API
+const prAuthorCache = {}
+async function resolveAuthorForPR(prNumber) {
+  if (prAuthorCache[prNumber] !== undefined) return prAuthorCache[prNumber]
+
+  if (!ghToken) {
+    prAuthorCache[prNumber] = null
+    return null
+  }
+
+  try {
+    const res = await fetch(
+      `https://api.github.com/repos/TanStack/router/pulls/${prNumber}`,
+      { headers: { Authorization: `token ${ghToken}` } },
+    )
+    const data = await res.json()
+    const login = data?.user?.login || null
+    prAuthorCache[prNumber] = login
+    return login
+  } catch {
+    prAuthorCache[prNumber] = null
+    return null
   }
 }

-// Append author info to changelog lines that contain commit hashes
+// Append author info to changelog lines that contain PR refs or commit hashes
 async function appendAuthors(content) {
   const lines = content.split('\n')
   const result = []

   for (const line of lines) {
-    // Match commit hash links like [`9a4d924`](url)
-    const commitMatch = line.match(/\[`([a-f0-9]{7,})`\]/)
-    if (commitMatch && line.startsWith('- ')) {
-      const author = await resolveAuthorForCommit(commitMatch[1])
-      result.push(author ? `${line}${author}` : line)
-    } else {
+    if (!line.startsWith('- ')) {
       result.push(line)
+      continue
+    }
+
+    // Try PR reference first: ([#6891](url))
+    const prMatch = line.match(/\[#(\d+)\]/)
+    if (prMatch) {
+      const username = await resolveAuthorForPR(prMatch[1])
+      result.push(username ? `${line} by @${username}` : line)
+      continue
+    }
+
+    // Fall back to commit hash: [`9a4d924`](url)
+    const commitMatch = line.match(/\[`([a-f0-9]{7,})`\]/)
+    if (commitMatch) {
+      const username = await resolveAuthorForCommit(commitMatch[1])
+      result.push(username ? `${line} by @${username}` : line)
+      continue
     }
+
+    result.push(line)
   }

   return result.join('\n')
PATCH

echo "Patch applied successfully."
