#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "gh api graphql -f query='{ repository(owner: \"<OWNER>\", name: \"<REPO>\") { pullRe" ".opencode/skills/qtpass-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-github/SKILL.md b/.opencode/skills/qtpass-github/SKILL.md
@@ -340,7 +340,7 @@ When PR shows "All comments must be resolved" but you've fixed the issues:
 **1. Identify unresolved threads via GraphQL:**
 
 ```bash
-gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }' | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | "\(.id) \(.isResolved)"'
+gh api graphql -f query='{ repository(owner: "<OWNER>", name: "<REPO>") { pullRequest(number: <PR_NUMBER>) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }' | jq -r '.data.repository.pullRequest.reviewThreads.nodes[] | "\(.id) \(.isResolved)"'
 ```
 
 **2. Resolve threads programmatically:**
@@ -355,7 +355,7 @@ gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \"$THR
 
 ```bash
 # Submit a COMMENT review (not APPROVE if it's your own PR)
-gh api "repos/OWNER/REPO/pulls/N/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"
+gh api "repos/<OWNER>/<REPO>/pulls/<PR_NUMBER>/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"
 ```
 
 **4. Common causes:**
PATCH

echo "Gold patch applied."
