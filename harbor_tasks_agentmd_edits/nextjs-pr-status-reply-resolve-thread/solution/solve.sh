#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'reply-and-resolve-thread' scripts/pr-status.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.agents/skills/pr-status-triage/SKILL.md b/.agents/skills/pr-status-triage/SKILL.md
index aa800d5d72f3ca..6a06077142e193 100644
--- a/.agents/skills/pr-status-triage/SKILL.md
+++ b/.agents/skills/pr-status-triage/SKILL.md
@@ -19,7 +19,7 @@ Use this skill when the user asks about PR status, CI failures, or review commen
 3. Prioritize blocking jobs first: build, lint, types, then test jobs.
 4. Treat failures as real until disproven; check the "Known Flaky Tests" section before calling anything flaky.
 5. Reproduce locally with the same mode and env vars as CI.
-6. After addressing review comments, reply to the thread describing what was done, then resolve it. See `thread-N.md` files for ready-to-use commands.
+6. After addressing review comments, reply to the thread describing what was done, then resolve it. Use `reply-and-resolve-thread` to do both in one step, or use `reply-thread` + `resolve-thread` separately. See `thread-N.md` files for ready-to-use commands.
 7. When the only remaining failures are known flaky tests and no code changes are needed, retrigger the failing CI jobs with `gh run rerun <run-id> --failed`. Then wait 5 minutes and go back to step 1. Repeat this loop up to 5 times.

 ## Quick Commands
@@ -31,6 +31,14 @@ node scripts/pr-status.js [PR] --wait      # background mode, waits for CI to fi
 node scripts/pr-status.js --skip-flaky-check  # skip flaky test detection
 ```

+Thread interaction:
+
+```bash
+node scripts/pr-status.js reply-thread <threadNodeId> "<body>"           # reply to a review thread
+node scripts/pr-status.js resolve-thread <threadNodeId>                  # resolve a review thread
+node scripts/pr-status.js reply-and-resolve-thread <threadNodeId> "<body>"  # reply and resolve in one step
+```
+
 ## References

 - [workflow.md](./workflow.md) — prioritization, common failure patterns, resolving review threads
diff --git a/.agents/skills/pr-status-triage/workflow.md b/.agents/skills/pr-status-triage/workflow.md
index 2ff48f95f282c0..a47c1ce04a6881 100644
--- a/.agents/skills/pr-status-triage/workflow.md
+++ b/.agents/skills/pr-status-triage/workflow.md
@@ -39,6 +39,12 @@ After addressing a review comment (e.g., making the requested code change), or w
    node scripts/pr-status.js resolve-thread <threadNodeId>
    ```

+Or do both in one step:
+
+```bash
+node scripts/pr-status.js reply-and-resolve-thread <threadNodeId> "Done -- <description of changes>"
+```
+
 The ready-to-use commands with the correct thread IDs are at the bottom of each `thread-N.md` file in `scripts/pr-status/`.

 **Important:** Always reply with a description of the actions taken before resolving. This gives the reviewer context about what changed.
diff --git a/scripts/pr-status.js b/scripts/pr-status.js
index eddf58b167c56e..5c7f5820839ae1 100644
--- a/scripts/pr-status.js
+++ b/scripts/pr-status.js
@@ -382,37 +382,66 @@ function getPRComments(prNumber) {

 function replyToThread(threadId, body) {
   body = ':robot: ' + body
-  const mutation = `
-    mutation($threadId: ID!, $body: String!) {
-      addPullRequestReviewThreadReply(input: {
-        pullRequestReviewThreadId: $threadId,
-        body: $body
-      }) {
-        comment {
-          id
-          url
+
+  // Step 1: Look up the PR number and first comment's databaseId from the
+  // thread's GraphQL node ID. The REST reply endpoint requires both.
+  const lookupQuery = `
+    query($id: ID!) {
+      node(id: $id) {
+        ... on PullRequestReviewThread {
+          pullRequest {
+            number
+          }
+          comments(first: 1) {
+            nodes {
+              databaseId
+            }
+          }
         }
       }
     }
   `
+  let prNumber, commentDatabaseId
+  try {
+    const lookupOutput = execFileSync(
+      'gh',
+      ['api', 'graphql', '-f', `query=${lookupQuery}`, '-f', `id=${threadId}`],
+      { encoding: 'utf8' }
+    ).trim()
+    const lookupData = JSON.parse(lookupOutput)
+    const thread = lookupData.data.node
+    if (!thread || !thread.pullRequest || !thread.comments?.nodes?.[0]) {
+      console.error(`Could not resolve thread node ID: ${threadId}`)
+      process.exit(1)
+    }
+    prNumber = thread.pullRequest.number
+    commentDatabaseId = thread.comments.nodes[0].databaseId
+  } catch (error) {
+    console.error(
+      'Failed to look up thread info:',
+      error.stderr || error.message
+    )
+    process.exit(1)
+  }
+
+  // Step 2: Post the reply via REST. Unlike the GraphQL mutation
+  // addPullRequestReviewThreadReply, this endpoint always publishes the reply
+  // immediately — it is never attached to a pending/draft review.
   try {
     const output = execFileSync(
       'gh',
       [
         'api',
-        'graphql',
-        '-f',
-        `query=${mutation}`,
-        '-f',
-        `threadId=${threadId}`,
+        '--method',
+        'POST',
+        `/repos/vercel/next.js/pulls/${prNumber}/comments/${commentDatabaseId}/replies`,
         '-f',
         `body=${body}`,
       ],
       { encoding: 'utf8' }
     ).trim()
     const data = JSON.parse(output)
-    const comment = data.data.addPullRequestReviewThreadReply.comment
-    console.log(`Reply posted: ${comment.url}`)
+    console.log(`Reply posted: ${data.html_url}`)
   } catch (error) {
     console.error('Failed to reply to thread:', error.stderr || error.message)
     process.exit(1)
@@ -1066,6 +1095,11 @@ function generateThreadMd(thread, index) {
         '```',
         `node scripts/pr-status.js resolve-thread ${thread.id}`,
         '```',
+        '',
+        'Reply and resolve in one step:',
+        '```',
+        `node scripts/pr-status.js reply-and-resolve-thread ${thread.id} "Your reply here"`,
+        '```',
         ''
       )
     }
@@ -1526,6 +1560,20 @@ async function main() {
     return
   }

+  if (subcommand === 'reply-and-resolve-thread') {
+    const threadId = process.argv[3]
+    const body = process.argv[4]
+    if (!threadId || !body) {
+      console.error(
+        'Usage: node scripts/pr-status.js reply-and-resolve-thread <threadNodeId> <body>'
+      )
+      process.exit(1)
+    }
+    replyToThread(threadId, body)
+    resolveThread(threadId)
+    return
+  }
+
   // Parse CLI arguments
   const args = process.argv.slice(2)
   const waitFlag = args.includes('--wait')

PATCH

echo "Patch applied successfully."
