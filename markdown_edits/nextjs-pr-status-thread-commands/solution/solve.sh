#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'reply-thread' scripts/pr-status.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.agents/skills/pr-status-triage/SKILL.md b/.agents/skills/pr-status-triage/SKILL.md
index f6afda36501077..2b8d35fd203cb6 100644
--- a/.agents/skills/pr-status-triage/SKILL.md
+++ b/.agents/skills/pr-status-triage/SKILL.md
@@ -19,6 +19,7 @@ Use this skill when the user asks about PR status, CI failures, or review commen
 3. Prioritize blocking jobs first: build, lint, types, then test jobs.
 4. Treat failures as real until disproven; check the "Known Flaky Tests" section before calling anything flaky.
 5. Reproduce locally with the same mode and env vars as CI.
+6. After addressing review comments, reply to the thread describing what was done, then resolve it. See `thread-N.md` files for ready-to-use commands.

 ## Quick Commands

diff --git a/.agents/skills/pr-status-triage/workflow.md b/.agents/skills/pr-status-triage/workflow.md
index 5307ab74f42eca..4626dfc95eebba 100644
--- a/.agents/skills/pr-status-triage/workflow.md
+++ b/.agents/skills/pr-status-triage/workflow.md
@@ -25,3 +25,20 @@
 - test failures:
   - Run the exact failing test file locally
   - Match dev vs start mode to the CI job
+
+## Resolving Review Threads
+
+After addressing a review comment (e.g., making the requested code change):
+
+1. Reply to the thread describing what action was taken:
+   ```bash
+   node scripts/pr-status.js reply-thread <threadNodeId> "Done -- <description of changes>"
+   ```
+2. Then resolve the thread:
+   ```bash
+   node scripts/pr-status.js resolve-thread <threadNodeId>
+   ```
+
+The ready-to-use commands with the correct thread IDs are at the bottom of each `thread-N.md` file in `scripts/pr-status/`.
+
+**Important:** Always reply with a description of the actions taken before resolving. This gives the reviewer context about what changed.
diff --git a/scripts/pr-status.js b/scripts/pr-status.js
index e3ebfbec5041a2..1c824e5ad24713 100644
--- a/scripts/pr-status.js
+++ b/scripts/pr-status.js
@@ -1,4 +1,4 @@
-const { execSync, spawn } = require('child_process')
+const { execSync, execFileSync, spawn } = require('child_process')
 const fs = require('fs/promises')
 const path = require('path')

@@ -325,6 +325,7 @@ function getPRReviewThreads(prNumber) {
         pullRequest(number:${prNumber}) {
           reviewThreads(first:100) {
             nodes {
+              id
               isResolved
               path
               line
@@ -366,6 +367,87 @@ function getPRComments(prNumber) {
   }
 }

+// ============================================================================
+// Thread Interaction Functions
+// ============================================================================
+
+function replyToThread(threadId, body) {
+  const mutation = `
+    mutation($threadId: ID!, $body: String!) {
+      addPullRequestReviewThreadReply(input: {
+        pullRequestReviewThreadId: $threadId,
+        body: $body
+      }) {
+        comment {
+          id
+          url
+        }
+      }
+    }
+  `
+  try {
+    const output = execFileSync(
+      'gh',
+      [
+        'api',
+        'graphql',
+        '-f',
+        `query=${mutation}`,
+        '-f',
+        `threadId=${threadId}`,
+        '-f',
+        `body=${body}`,
+      ],
+      { encoding: 'utf8' }
+    ).trim()
+    const data = JSON.parse(output)
+    const comment = data.data.addPullRequestReviewThreadReply.comment
+    console.log(`Reply posted: ${comment.url}`)
+  } catch (error) {
+    console.error('Failed to reply to thread:', error.stderr || error.message)
+    process.exit(1)
+  }
+}
+
+function resolveThread(threadId) {
+  const mutation = `
+    mutation($threadId: ID!) {
+      resolveReviewThread(input: {
+        threadId: $threadId
+      }) {
+        thread {
+          id
+          isResolved
+        }
+      }
+    }
+  `
+  try {
+    const output = execFileSync(
+      'gh',
+      [
+        'api',
+        'graphql',
+        '-f',
+        `query=${mutation}`,
+        '-f',
+        `threadId=${threadId}`,
+      ],
+      { encoding: 'utf8' }
+    ).trim()
+    const data = JSON.parse(output)
+    const thread = data.data.resolveReviewThread.thread
+    if (thread.isResolved) {
+      console.log(`Thread ${threadId} resolved successfully.`)
+    } else {
+      console.log('Warning: Thread may not have been resolved.')
+    }
+  } catch (error) {
+    console.error('Failed to resolve thread:', error.stderr || error.message)
+    process.exit(1)
+  }
+}
+
 // ============================================================================
 // Log Parsing Functions
 // ============================================================================
@@ -953,6 +1035,27 @@ function generateThreadMd(thread, index) {
     lines.push(`[View on GitHub](${comment.url})`, '', '---', '')
   }

+  // Add commands section
+  if (thread.id) {
+    lines.push('## Commands', '')
+    lines.push(
+      'Reply to this thread:',
+      '```',
+      `node scripts/pr-status.js reply-thread ${thread.id} "Your reply here"`,
+      '```',
+      ''
+    )
+    if (!thread.isResolved) {
+      lines.push(
+        'Resolve this thread:',
+        '```',
+        `node scripts/pr-status.js resolve-thread ${thread.id}`,
+        '```',
+        ''
+      )
+    }
+  }
+
   return lines.join('\n')
 }

@@ -1102,8 +1205,36 @@ async function getFlakyTests(currentBranch, runsToCheck = 5) {
 // ============================================================================

 async function main() {
+  // Dispatch subcommands
+  const subcommand = process.argv[2]
+
+  if (subcommand === 'reply-thread') {
+    const threadId = process.argv[3]
+    const body = process.argv[4]
+    if (!threadId || !body) {
+      console.error(
+        'Usage: node scripts/pr-status.js reply-thread <threadNodeId> <body>'
+      )
+      process.exit(1)
+    }
+    replyToThread(threadId, body)
+    return
+  }
+
+  if (subcommand === 'resolve-thread') {
+    const threadId = process.argv[3]
+    if (!threadId) {
+      console.error(
+        'Usage: node scripts/pr-status.js resolve-thread <threadNodeId>'
+      )
+      process.exit(1)
+    }
+    resolveThread(threadId)
+    return
+  }
+
   // Parse CLI argument for PR number
-  const prNumberArg = process.argv[2]
+  const prNumberArg = subcommand

   // Step 1: Delete and recreate output directory
   console.log('Cleaning output directory...')

PATCH

echo "Patch applied successfully."
