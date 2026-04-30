#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotency guard
if grep -qF "4. **Mark as In Progress**: When starting to plan or implement an issue, immedia" ".agents/skills/linear/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/linear/SKILL.md b/.agents/skills/linear/SKILL.md
@@ -20,9 +20,11 @@ This is NON-NEGOTIABLE. Skipping Linear comments is a workflow violation.
 ## Workflow
 
 1. **Retrieve issue details** before starting: `mcp__linear-server__get_issue`
-2. **Check for sub-issues**: Use `mcp__linear-server__list_issues` with `parentId` filter
-3. **Update issue status** when completing: `mcp__linear-server__update_issue`
-4. **Add completion comment** (REQUIRED): `mcp__linear-server__create_comment`
+2. **Read images**: If the issue description contains images, MUST use `mcp__linear-server__extract_images` to read image content for full context
+3. **Check for sub-issues**: Use `mcp__linear-server__list_issues` with `parentId` filter
+4. **Mark as In Progress**: When starting to plan or implement an issue, immediately update status to **"In Progress"** via `mcp__linear-server__update_issue`
+5. **Update issue status** when completing: `mcp__linear-server__update_issue`
+6. **Add completion comment** (REQUIRED): `mcp__linear-server__create_comment`
 
 ## Creating Issues
 
PATCH

echo "Gold patch applied."
