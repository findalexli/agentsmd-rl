#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jira-skill

# Idempotency guard
if grep -qF "description: \"Use when interacting with Jira issues - searching, creating, updat" "skills/jira-communication/SKILL.md" && grep -qF "description: \"Use when writing Jira descriptions or comments, converting Markdow" "skills/jira-syntax/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/jira-communication/SKILL.md b/skills/jira-communication/SKILL.md
@@ -1,17 +1,6 @@
 ---
 name: jira-communication
-description: >
-  Jira API operations via Python CLI scripts. AUTOMATICALLY TRIGGER when user
-  mentions Jira URLs (https://jira.*/browse/*, https://*.atlassian.net/browse/*),
-  issue keys (PROJ-123), or asks about Jira issues. Use when Claude needs to:
-  (1) Search issues with JQL queries, (2) Get or update issue details,
-  (3) Create new issues, (4) Transition issue status (e.g., "To Do" → "Done"),
-  (5) Add comments, (6) Log work time (worklogs), (7) List sprints and sprint issues,
-  (8) List boards and board issues, (9) Create or list issue links,
-  (10) Discover available Jira fields, (11) Get user profile information,
-  (12) Download attachments from issues.
-  If authentication fails, offer interactive credential setup via jira-setup.py.
-  Supports both Jira Cloud and Server/Data Center with automatic auth detection.
+description: "Use when interacting with Jira issues - searching, creating, updating, transitioning, commenting, logging work, downloading attachments, managing sprints, boards, issue links, fields, or users. Auto-triggers on Jira URLs and issue keys (PROJ-123)."
 allowed-tools: Bash(uv run scripts/*:*) Read
 ---
 
diff --git a/skills/jira-syntax/SKILL.md b/skills/jira-syntax/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: jira-syntax
-description: "Jira wiki markup syntax validation, templates, and formatting guidance. Use when: (1) Writing Jira issue descriptions or comments, (2) Converting Markdown to Jira wiki markup, (3) Requesting bug report or feature request templates, (4) Validating Jira syntax before submission, (5) Keywords like 'jira format', 'wiki markup', 'jira syntax', 'format for jira', (6) Ensuring content uses h2./h3. headings instead of Markdown ##, (7) Checking code blocks use {code:lang} not triple backticks, (8) Any task involving Jira text formatting"
+description: "Use when writing Jira descriptions or comments, converting Markdown to Jira wiki markup, using templates (bug reports, feature requests), or validating Jira syntax before submission."
 allowed-tools: Bash(scripts/validate-jira-syntax.sh:*) Read
 ---
 
PATCH

echo "Gold patch applied."
