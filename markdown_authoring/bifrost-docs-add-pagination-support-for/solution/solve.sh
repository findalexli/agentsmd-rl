#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bifrost

# Idempotency guard
if grep -qF "**Important:** `reviewThreads` returns at most 100 threads per request. PRs with" ".claude/skills/resolve-pr-comments/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/resolve-pr-comments/SKILL.md b/.claude/skills/resolve-pr-comments/SKILL.md
@@ -23,7 +23,7 @@ If no repo is specified, uses the current git repository's remote origin.
 ## Workflow Overview
 
 1. **Detect repository** - Get owner/repo from git remote or user input
-2. **Fetch unresolved comments** - Use GitHub GraphQL API (REST doesn't expose resolved status)
+2. **Fetch unresolved comments** - Use GitHub GraphQL API (REST doesn't expose resolved status). Paginate through `reviewThreads` (cursor-based) so all pages are checked when a PR has more than 100 threads.
 3. **Create tracking file** - Maintain state across the session
 4. **For each comment**:
    - Get full details and any existing replies
@@ -46,21 +46,27 @@ git remote get-url origin | sed -E 's|.*github.com[:/]([^/]+/[^/.]+)(\.git)?|\1|
 
 ## Step 2: Fetch Unresolved Comments (GraphQL)
 
-The REST API does NOT expose resolved/unresolved status. Use GraphQL:
+The REST API does NOT expose resolved/unresolved status. Use GraphQL.
+
+**Important:** `reviewThreads` returns at most 100 threads per request. PRs with many review threads (e.g. large CodeRabbit reviews) need **pagination** or you will only see the first 100 threads and miss unresolved ones on later pages. Always paginate until `pageInfo.hasNextPage` is false so the count and list are complete.
+
+### Single-page query (first 100 threads only)
 
 ```bash
 gh api graphql -f query='
 {
   repository(owner: "OWNER", name: "REPO") {
     pullRequest(number: PR_NUMBER) {
       reviewThreads(first: 100) {
+        pageInfo { hasNextPage endCursor }
         nodes {
           isResolved
           comments(first: 1) {
             nodes {
               databaseId
               path
               body
+              author { login }
             }
           }
         }
@@ -70,16 +76,73 @@ gh api graphql -f query='
 }'
 ```
 
-Extract unresolved comments:
+Extract unresolved (single page):
 ```bash
-... | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | "\(.comments.nodes[0].databaseId)|\(.comments.nodes[0].path)|\(.comments.nodes[0].body | gsub("\n"; " ") | .[0:100])"'
+... | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | "\(.comments.nodes[0].databaseId)|\(.comments.nodes[0].path)|\(.comments.nodes[0].author.login)"'
 ```
 
-Count unresolved:
+Avoid parsing `body` in the same jq pass if you paginate—comment bodies can contain control characters and break jq. Fetch full body per comment via REST when presenting (see Step 4).
+
+### Paginate to collect all unresolved threads
+
+Use cursor-based pagination so every thread is considered:
+
+1. First request: `reviewThreads(first: 100)` (no `after`).
+2. From the response: read `pageInfo.hasNextPage` and `pageInfo.endCursor`.
+3. Next request: `reviewThreads(first: 100, after: $endCursor)`.
+4. Append unresolved from this page to your list (id, path, author only).
+5. Repeat from step 2 until `hasNextPage` is false.
+
+Example loop (collects id|path|author for all unresolved; write to a file or variable):
+
 ```bash
-... | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length'
+CURSOR=""
+while true; do
+  if [ -z "$CURSOR" ]; then
+    RESP=$(gh api graphql -f query='
+      query {
+        repository(owner: "OWNER", name: "REPO") {
+          pullRequest(number: PR_NUMBER) {
+            reviewThreads(first: 100) {
+              pageInfo { hasNextPage endCursor }
+              nodes {
+                isResolved
+                comments(first: 1) {
+                  nodes { databaseId path author { login } }
+                }
+              }
+            }
+          }
+        }
+      }')
+  else
+    RESP=$(gh api graphql -f query='
+      query($after: String) {
+        repository(owner: "OWNER", name: "REPO") {
+          pullRequest(number: PR_NUMBER) {
+            reviewThreads(first: 100, after: $after) {
+              pageInfo { hasNextPage endCursor }
+              nodes {
+                isResolved
+                comments(first: 1) {
+                  nodes { databaseId path author { login } }
+                }
+              }
+            }
+          }
+        }
+      }' -f after="$CURSOR")
+  fi
+  # Append unresolved from this page (id|path|author only; no body to avoid control chars)
+  echo "$RESP" | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | .comments.nodes[0] | "\(.databaseId)|\(.path)|\(.author.login)"'
+  HAS_NEXT=$(echo "$RESP" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage')
+  CURSOR=$(echo "$RESP" | jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor // ""')
+  [ "$HAS_NEXT" != "true" ] || [ -z "$CURSOR" ] && break
+done
 ```
 
+Total unresolved count = number of lines output. Use the comment `databaseId` values to fetch full body via REST when presenting each comment (Step 4).
+
 ## Step 3: Create Tracking File
 
 Create at `/tmp/pr-review/pr-<NUMBER>-comments.md`:
@@ -152,21 +215,36 @@ gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments --paginate | jq '.[] | select(.
 4. Continue to next comment
 
 ### For REPLY (non-code responses like "out of scope", "intentional design"):
-These can be posted immediately since they don't require code verification:
+These can be posted immediately since they don't require code verification. Use the **replies** endpoint only (see below).
+
+## Reply endpoint (use this only)
+
+To reply to a review comment, use the dedicated replies endpoint. **Do not** use `POST .../pulls/PR_NUMBER/comments` with `in_reply_to` — that returns 422 (in_reply_to is not a permitted key for create review comment).
+
 ```bash
 gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies -X POST -f body="<your reply>"
 ```
 
+- `COMMENT_ID` is the numeric comment id (same as GraphQL `databaseId` from the thread's first comment).
+- Request body: only `body` (string). No `in_reply_to`, `commit_id`, or path params.
+
 ## Step 5b: Push and Reply to FIX comments
 
 After ALL comments have been addressed locally:
 
-1. Ask user to if they have pushed these changes to remote. Yes/No
-2. **Only after push succeeds**, reply to FIX comments:
+1. Ask user if they have pushed these changes to remote. Yes/No
+2. **Only after push succeeds**, reply to each FIX comment using the replies endpoint:
    ```bash
    gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies -X POST -f body="Fixed - <description of change>. See updated code."
    ```
 
+### Batch workflow (fix all → push → post all)
+
+If the user says e.g. "resolve all comments then push then post", you may:
+1. Apply all FIX and REPLY decisions locally (with user approval per comment or bulk approval).
+2. Ask user to push.
+3. After push, post all replies in sequence: FIX replies first, then any REPLY-only replies, using the same `.../comments/COMMENT_ID/replies` endpoint for each.
+
 ### Common Reply Templates
 
 **Out of scope:**
@@ -196,13 +274,14 @@ This is solved, can you check and resolve if done properly?
 
 ## Step 6: Verify Resolution
 
-After addressing comments, check remaining count:
+After addressing comments, check remaining unresolved count. If the PR has more than 100 review threads, use the same pagination loop as in Step 2 and count unresolved across all pages; a single-page query only sees the first 100 threads.
 
+Single-page check (first 100 threads only):
 ```bash
 gh api graphql -f query='...' | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length'
 ```
 
-If count is 0, report success. If comments remain:
+If count is 0 (across all pages), report success. If comments remain:
 - Some bots (like CodeRabbit) take time to auto-resolve
 - User may need to push code changes first
 - Re-run the workflow to address remaining comments
@@ -222,4 +301,5 @@ If count is 0, report success. If comments remain:
 - If `gh` not authenticated: `gh auth login`
 - If repo not found: verify owner/repo spelling
 - If PR not found: verify PR number exists
-- If comment ID invalid: re-fetch unresolved comments (may have been resolved)
\ No newline at end of file
+- If comment ID invalid: re-fetch unresolved comments (may have been resolved)
+- If reply returns 422 "in_reply_to is not a permitted key": you are using the wrong endpoint. Use `POST .../pulls/PR_NUMBER/comments/COMMENT_ID/replies` with only `-f body="..."`, not the create-comment endpoint.
\ No newline at end of file
PATCH

echo "Gold patch applied."
