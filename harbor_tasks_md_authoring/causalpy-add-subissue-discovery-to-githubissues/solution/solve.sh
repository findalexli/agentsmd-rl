#!/usr/bin/env bash
set -euo pipefail

cd /workspace/causalpy

# Idempotency guard
if grep -qF "Always check whether an issue has native sub-issues. The `trackedIssues` / `trac" ".github/skills/github-issues/reference/issue-evaluation.md" && grep -qF "When evaluating an issue that may already have sub-issues, always use the `subIs" ".github/skills/github-issues/reference/parent-child-issues.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/github-issues/reference/issue-evaluation.md b/.github/skills/github-issues/reference/issue-evaluation.md
@@ -10,10 +10,26 @@ description: Analyze an issue, check current relevance, and propose next steps o
 gh issue view <issue_number> --json number,title,body,state,labels,comments,assignees
 ```
 
+## Check for sub-issues (native hierarchy)
+
+Always check whether an issue has native sub-issues. The `trackedIssues` / `trackedInIssues` GraphQL fields only cover older markdown task-list tracking and will miss native sub-issues.
+
+```bash
+gh api graphql -f query='query {
+  repository(owner:"<owner>", name:"<repo>") {
+    issue(number: <issue_number>) {
+      subIssues(first: 50) { nodes { number title state url } }
+      parent { number title state url }
+    }
+  }
+}'
+```
+
 ## Analyze context
 - Extract the problem statement and acceptance criteria
 - Summarize discussion history and blockers
 - Identify affected files/modules
+- Review sub-issues (if any) for work breakdown and progress
 
 ## Assess relevance
 - Search codebase for mentioned APIs or modules
diff --git a/.github/skills/github-issues/reference/parent-child-issues.md b/.github/skills/github-issues/reference/parent-child-issues.md
@@ -91,7 +91,24 @@ gh api graphql \
   -f sub='<CHILD_NODE_ID>'
 ```
 
-## 6) Verify links rendered correctly
+## 6) Discover existing sub-issues
+
+When evaluating an issue that may already have sub-issues, always use the `subIssues` GraphQL field. Do **not** use `trackedIssues` / `trackedInIssues` -- those only cover older markdown task-list tracking and will miss native sub-issues.
+
+```bash
+gh api graphql -f query='query {
+  repository(owner:"<owner>", name:"<repo>") {
+    issue(number: <issue_number>) {
+      subIssues(first: 50) {
+        nodes { number title state url }
+      }
+      parent { number title state url }
+    }
+  }
+}'
+```
+
+## 7) Verify links rendered correctly
 
 ```bash
 gh api graphql -f query='query {
PATCH

echo "Gold patch applied."
