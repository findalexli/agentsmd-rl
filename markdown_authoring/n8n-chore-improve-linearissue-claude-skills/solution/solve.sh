#!/usr/bin/env bash
set -euo pipefail

cd /workspace/n8n

# Idempotency guard
if grep -qF "> One or more of your remotes point to the **public** `n8n-io/n8n` repo. Mixed r" ".claude/plugins/n8n/skills/linear-issue/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/plugins/n8n/skills/linear-issue/SKILL.md b/.claude/plugins/n8n/skills/linear-issue/SKILL.md
@@ -50,7 +50,25 @@ Use the Linear MCP tools to fetch the issue details and comments together:
 
 Both calls should be made together in the same step to gather the complete context upfront.
 
-### 2. Analyze Attachments and Media (MANDATORY)
+### 2. Check for Private/Security Issues (MANDATORY — do this before anything else)
+
+After fetching the issue, immediately check its labels:
+
+1. Look at the labels returned with the issue.
+2. If any label is **`n8n-private`**:
+   a. Run `git remote -v` (via Bash) to list all configured remotes.
+   b. If **any** remote URL contains `n8n-io/n8n` without the `-private` suffix (i.e. matches the public repo), **stop immediately** and tell the user:
+
+   > **This issue is marked `n8n-private` and must be developed in a clean clone of the private repository.**
+   >
+   > One or more of your remotes point to the **public** `n8n-io/n8n` repo. Mixed remotes are not allowed — you must work in a **separate local clone** of `n8n-io/n8n-private` with no references to the public repo.
+   > For the full process, see: https://www.notion.so/n8n/Processing-critical-high-security-bugs-vulnerabilities-in-private-2f45b6e0c94f803da806f472111fb1a5
+
+   Do **not** continue with any further steps — return after showing this message.
+
+3. If the label is not present, or all remotes point exclusively to `n8n-io/n8n-private`, continue normally.
+
+### 3. Analyze Attachments and Media (MANDATORY)
 
 **IMPORTANT:** This step is NOT optional. You MUST scan and fetch all visual content from BOTH the issue description AND all comments.
 
@@ -74,7 +92,7 @@ Both calls should be made together in the same step to gather the complete conte
 	- Summarize key points, timestamps, and any demonstrated issues
 3. Loom videos often contain crucial reproduction steps and context that text alone cannot convey
 
-### 3. Fetch Related Context
+### 4. Fetch Related Context
 
 **Related Linear Issues:**
 - Use `mcp__linear__get_issue` for any issues mentioned in relations (blocking, blocked by, related, duplicates)
@@ -90,14 +108,14 @@ Both calls should be made together in the same step to gather the complete conte
 - If Notion links are present, use `mcp__notion__notion-fetch` with the Notion URL or page ID to retrieve document content
 - Summarize relevant documentation
 
-### 4. Review Comments
+### 5. Review Comments
 
 Comments were already fetched in Step 1. Review them for:
 - Additional context and discussion history
-- Any attachments or media linked in comments (process in Step 2)
+- Any attachments or media linked in comments (process in Step 3)
 - Clarifications or updates to the original issue description
 
-### 5. Identify Affected Node (if applicable)
+### 6. Identify Affected Node (if applicable)
 
 Determine whether this issue is specific to a particular n8n node (e.g. a trigger, action, or tool node). Look for clues in:
 - The issue title (e.g. "Linear trigger", "Slack node", "HTTP Request")
@@ -125,7 +143,7 @@ If the issue is node-specific:
 
 3. If the node is **not found** in the popularity file, note that it may be a community node or a very new/niche node.
 
-### 6. Assess Effort/Complexity
+### 7. Assess Effort/Complexity
 
 After gathering all context, assess the effort required to fix/implement the issue. Use the following T-shirt sizes:
 
@@ -147,7 +165,7 @@ To make this assessment, consider:
 
 Provide the T-shirt size along with a brief justification explaining the key factors that drove the estimate.
 
-### 7. Present Summary
+### 8. Present Summary
 
 **Before presenting, verify you have completed:**
 - [ ] Downloaded and viewed ALL images in the description AND comments
PATCH

echo "Gold patch applied."
