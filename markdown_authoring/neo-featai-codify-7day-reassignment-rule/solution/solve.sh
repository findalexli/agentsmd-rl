#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "- **If `now - lastQualifyingActivity >= 7 days`:** Proceed with self-serve reass" ".agent/skills/ticket-intake/references/ticket-intake-workflow.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/ticket-intake/references/ticket-intake-workflow.md b/.agent/skills/ticket-intake/references/ticket-intake-workflow.md
@@ -39,13 +39,18 @@ If the ticket passes validation and yields a positive ROI, you MUST execute the
 
 ### 3a. Claim Ownership (Auto-Assign)
 
-Signal to the Swarm that this ticket is actively being worked. Use the `manage_issue_assignees` MCP tool to assign the ticket to yourself:
-
-```
-manage_issue_assignees(action: 'add', issue_number: N, assignees: ['@me'])
-```
-
-The `@me` shortcut resolves to the authenticated GitHub user — no hardcoded usernames. This prevents duplicate pickup by concurrent agents and provides human visibility into active work.
+Signal to the Swarm that this ticket is actively being worked. Before assigning yourself, you MUST verify that the ticket is not already owned by another active agent or human.
+
+1. **Query Existing Assignee:** Read the `assignees` array from the ticket's frontmatter (via `get_local_issue_by_id`) or GitHub.
+2. **If Empty:** Proceed with assignment:
+   ```
+   manage_issue_assignees(action: 'add', issue_number: N, assignees: ['@me'])
+   ```
+   The `@me` shortcut resolves to the authenticated GitHub user. This prevents duplicate pickup by concurrent agents and provides human visibility.
+3. **If Assigned (The 7-Day Rule):** Per the Neo.mjs `CONTRIBUTING.md`, tickets are protected from being hijacked unless the current assignee has gone stale.
+   - Compute `lastQualifyingActivity`: The most recent comment from the current assignee OR from any maintainer (`@neo-opus-4-7`, `@neo-gemini-3-1-pro`, or contributor with write permissions) acknowledging in-progress work. (Random observer comments do NOT count).
+   - **If `now - lastQualifyingActivity < 7 days`:** BLOCK pickup. Post a comment requesting transfer or clarification, do NOT self-assign, and halt the intake protocol.
+   - **If `now - lastQualifyingActivity >= 7 days`:** Proceed with self-serve reassignment. You MUST post a mandatory attribution comment first: *"Picking up per 7-day rule; previous assignee @X; last qualifying activity <ISO-8601 timestamp>."* Then call `manage_issue_assignees` to add `@me`.
 
 ### 3b. Branch-Before-Code Gate
 
PATCH

echo "Gold patch applied."
