#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jira-skill

# Idempotency guard
if grep -qF "uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-search.py query \"project = PROJ ORD" "skills/jira-communication/SKILL.md" && grep -qF "- `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh` - Automated syntax check" "skills/jira-syntax/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/jira-communication/SKILL.md b/skills/jira-communication/SKILL.md
@@ -14,19 +14,17 @@ allowed-tools: Bash(python:*) Bash(uv:*) Bash(curl:*) Read Write
 
 CLI scripts via `uv run`. All support `--help`, `--json`, `--quiet`, `--debug`.
 
-**Paths** are relative to `skills/jira-communication/`.
-
 ## Auto-Trigger
 
-On Jira URL or issue key (PROJ-123) → `jira-issue.py get PROJ-123`. Auth issues → `jira-setup.py`.
+On Jira URL or issue key (PROJ-123) → run `jira-issue.py get`. Auth issues → `jira-setup.py`.
 
 ## Scripts
 
 **Core**: `jira-issue.py` (get/update/delete), `jira-search.py` (JQL), `jira-worklog.py`, `jira-attachment.py`, `jira-setup.py`, `jira-validate.py`
 **Workflow**: `jira-create.py`, `jira-transition.py`, `jira-comment.py` (add/edit/delete/list), `jira-move.py`, `jira-sprint.py`, `jira-board.py`
 **Utility**: `jira-user.py`, `jira-fields.py` (search/types), `jira-link.py`
 
-All in `scripts/core/`, `scripts/workflow/`, or `scripts/utility/`.
+Scripts in `${CLAUDE_SKILL_DIR}/scripts/` under `core/`, `workflow/`, or `utility/`.
 
 
 ## Execution Style
@@ -35,52 +33,52 @@ All in `scripts/core/`, `scripts/workflow/`, or `scripts/utility/`.
 
 Global flags go **before** the subcommand:
 ```bash
-uv run scripts/core/jira-issue.py --json get PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py --json get PROJ-123
 ```
 
 ## Common Tasks
 
 ```bash
 # Read issue
-uv run scripts/core/jira-issue.py get PROJ-123
-uv run scripts/core/jira-issue.py --json get PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py get PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py --json get PROJ-123
 
 # Search (use -f for fields, -n for limit)
-uv run scripts/core/jira-search.py query "assignee = currentUser() AND status != Closed"
-uv run scripts/core/jira-search.py query "project = PROJ ORDER BY updated DESC" -n 5 -f key,summary,status,priority
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-search.py query "assignee = currentUser() AND status != Closed"
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-search.py query "project = PROJ ORDER BY updated DESC" -n 5 -f key,summary,status,priority
 
 # Update fields / assign (--fields-json for description and custom fields)
-uv run scripts/core/jira-issue.py update PROJ-123 --assignee me
-uv run scripts/core/jira-issue.py update PROJ-123 --priority Critical --summary "New title"
-uv run scripts/core/jira-issue.py update PROJ-123 --fields-json '{"description": "New desc"}'
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --assignee me
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --priority Critical --summary "New title"
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py update PROJ-123 --fields-json '{"description": "New desc"}'
 
 # Delete issue (use --dry-run to preview, --delete-subtasks for parent issues)
-uv run scripts/core/jira-issue.py delete PROJ-123 --dry-run
-uv run scripts/core/jira-issue.py delete PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py delete PROJ-123 --dry-run
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-issue.py delete PROJ-123
 
 # Comment (add/edit/list — use --json list to get IDs for edit/delete)
-uv run scripts/workflow/jira-comment.py add PROJ-123 "Comment text"
-cat comment.txt | uv run scripts/workflow/jira-comment.py add PROJ-123 -
-uv run scripts/workflow/jira-comment.py --json list PROJ-123
-uv run scripts/workflow/jira-comment.py edit PROJ-123 COMMENT_ID "Updated text"
-uv run scripts/workflow/jira-comment.py delete PROJ-123 COMMENT_ID --dry-run
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-comment.py add PROJ-123 "Comment text"
+cat comment.txt | uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-comment.py add PROJ-123 -
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-comment.py --json list PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-comment.py edit PROJ-123 COMMENT_ID "Updated text"
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-comment.py delete PROJ-123 COMMENT_ID --dry-run
 
 # Transition (use "list" to see available transitions)
-uv run scripts/workflow/jira-transition.py list PROJ-123
-uv run scripts/workflow/jira-transition.py do PROJ-123 "In Progress"
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-transition.py list PROJ-123
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-transition.py do PROJ-123 "In Progress"
 
 # Log work
-uv run scripts/core/jira-worklog.py add PROJ-123 2h --comment "Work done"
+uv run ${CLAUDE_SKILL_DIR}/scripts/core/jira-worklog.py add PROJ-123 2h --comment "Work done"
 
 # Create (--type auto-resolves to subtask when --parent given)
-uv run scripts/workflow/jira-create.py issue PROJ "Summary" --type Task
-uv run scripts/workflow/jira-create.py issue PROJ "Summary" --type Bug --parent PROJ-100
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-create.py issue PROJ "Summary" --type Task
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-create.py issue PROJ "Summary" --type Bug --parent PROJ-100
 
 # Move / change type / link
-uv run scripts/workflow/jira-move.py issue NRS-100 SRVUC
-uv run scripts/workflow/jira-move.py issue NRS-100 NRS --issue-type Task
-uv run scripts/utility/jira-link.py create PROJ-123 PROJ-456 --type "Blocks"
-uv run scripts/utility/jira-fields.py types PROJ
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-move.py issue NRS-100 SRVUC
+uv run ${CLAUDE_SKILL_DIR}/scripts/workflow/jira-move.py issue NRS-100 NRS --issue-type Task
+uv run ${CLAUDE_SKILL_DIR}/scripts/utility/jira-link.py create PROJ-123 PROJ-456 --type "Blocks"
+uv run ${CLAUDE_SKILL_DIR}/scripts/utility/jira-fields.py types PROJ
 ```
 
 `--assignee me` resolves to the authenticated user.
diff --git a/skills/jira-syntax/SKILL.md b/skills/jira-syntax/SKILL.md
@@ -46,7 +46,7 @@ Sections: Overview, User Stories, Acceptance Criteria, Technical Approach, Succe
 
 Run before submitting to Jira:
 ```bash
-scripts/validate-jira-syntax.sh path/to/content.txt
+${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh path/to/content.txt
 ```
 
 ### Validation Checklist
@@ -75,13 +75,13 @@ scripts/validate-jira-syntax.sh path/to/content.txt
 **Workflow:**
 1. Get template from jira-syntax
 2. Fill content using Jira wiki markup
-3. Validate with `scripts/validate-jira-syntax.sh`
-4. Submit via jira-communication scripts (e.g., `uv run scripts/workflow/jira-create.py`)
+3. Validate with `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh`
+4. Submit via jira-communication skill
 
 ## References
 
 - `references/jira-syntax-quick-reference.md` - Complete syntax documentation
 - `templates/bug-report-template.md` - Bug report template
 - `templates/feature-request-template.md` - Feature request template
-- `scripts/validate-jira-syntax.sh` - Automated syntax checker
+- `${CLAUDE_SKILL_DIR}/scripts/validate-jira-syntax.sh` - Automated syntax checker
 - [Official Jira Wiki Markup](https://jira.atlassian.com/secure/WikiRendererHelpAction.jspa?section=all)
PATCH

echo "Gold patch applied."
