#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cog-second-brain

# Idempotency guard
if grep -qF "2. Store this value and use it for ALL timestamp fields (`created:` frontmatter " ".claude/skills/braindump/SKILL.md" && grep -qF "3. NEVER guess or fabricate the time \u2014 always use the value returned by the `dat" ".claude/skills/daily-brief/SKILL.md" && grep -qF "3. NEVER guess or fabricate the time \u2014 always use the value returned by the `dat" ".claude/skills/knowledge-consolidation/SKILL.md" && grep -qF "3. NEVER guess or fabricate the time \u2014 always use the value returned by the `dat" ".claude/skills/weekly-checkin/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/braindump/SKILL.md b/.claude/skills/braindump/SKILL.md
@@ -39,6 +39,12 @@ Transform raw thoughts into strategic intelligence through quick capture, system
    - Use user's name for friendly communication
    - Read `03-professional/COMPETITIVE-WATCHLIST.md` if it exists for competitive intelligence detection
 
+**Get current timestamp (REQUIRED before generating any files):**
+
+1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
+2. Store this value and use it for ALL timestamp fields (`created:` frontmatter AND filename `HHMM` component)
+3. NEVER guess or fabricate the time — always use the value returned by the `date` command
+
 ## Process Flow
 
 ### 1. User Interaction & Input Collection
diff --git a/.claude/skills/daily-brief/SKILL.md b/.claude/skills/daily-brief/SKILL.md
@@ -40,6 +40,12 @@ Find verified, relevant news for personalized daily briefings with strict verifi
    - Use topics to curate relevant news
    - Connect news to user's active projects when relevant
 
+**Get current timestamp (REQUIRED before generating any files):**
+
+1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
+2. Store this value and use it for the `created:` frontmatter field
+3. NEVER guess or fabricate the time — always use the value returned by the `date` command
+
 ## Process Flow
 
 ### 1. Gather Context
diff --git a/.claude/skills/knowledge-consolidation/SKILL.md b/.claude/skills/knowledge-consolidation/SKILL.md
@@ -21,6 +21,14 @@ Transform scattered insights from braindumps, daily briefs, and check-ins into c
 - If `agent_mode: team` — delegate scanning and pattern extraction to parallel sub-agents (e.g., one per domain: personal braindumps, professional braindumps, project-specific content, daily briefs). Each agent identifies themes and patterns, then a synthesis agent combines findings into frameworks.
 - If `agent_mode: solo` (default) — handle all scanning, pattern recognition, and framework building directly. No delegation.
 
+## Pre-Flight Check
+
+**Get current timestamp (REQUIRED before generating any files):**
+
+1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
+2. Store this value and use it for the `created:` frontmatter field
+3. NEVER guess or fabricate the time — always use the value returned by the `date` command
+
 ## Process Flow
 
 ### 1. Data Gathering
diff --git a/.claude/skills/weekly-checkin/SKILL.md b/.claude/skills/weekly-checkin/SKILL.md
@@ -30,6 +30,12 @@ Comprehensive weekly review and analysis integrating insights across all domains
    - Read active projects to review project-specific progress
    - Tailor reflection questions to user's role and projects
 
+**Get current timestamp (REQUIRED before generating any files):**
+
+1. Run `date '+%Y-%m-%d %H:%M'` using Bash to get the actual current date and time
+2. Store this value and use it for the `created:` frontmatter field
+3. NEVER guess or fabricate the time — always use the value returned by the `date` command
+
 ## Process Flow
 
 ### 1. Gather Context
PATCH

echo "Gold patch applied."
