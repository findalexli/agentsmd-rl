#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cog-second-brain

# Idempotency guard
if grep -qF "2. **Headline match (fallback):** If the URL is different but the headline descr" ".claude/skills/daily-brief/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/daily-brief/SKILL.md b/.claude/skills/daily-brief/SKILL.md
@@ -66,6 +66,22 @@ Collect the information needed for personalized curation:
 - Read `03-professional/COMPETITIVE-WATCHLIST.md` (if exists) for:
   - Companies/people to track
 
+#### Deduplication — Previous Brief Scan
+
+Read up to 3 most recent daily briefs from `01-daily/briefs/` (most recent first):
+- Extract `dedup_urls` from their frontmatter (if present)
+- Also scan their headlines/story titles as semantic fallback for cross-source matching
+- Build a set of **covered stories** to avoid repeating
+
+**Matching rules (in priority order):**
+1. **URL match (primary):** If a candidate story's main source URL already appears in `dedup_urls`, it's a known story
+2. **Headline match (fallback):** If the URL is different but the headline describes the same event as a previous story, treat as duplicate — this catches the same story reported by different outlets
+
+During news research (Step 2), apply dedup rules:
+- **Skip** stories already covered unless there is a **material update** (new data, resolution, escalation, reversal)
+- If including an update, prefix with "**Update:** _first covered [date]_"
+- Stories older than 3 briefs are eligible for re-inclusion if still developing
+
 ### 2. News Research and Curation
 
 Apply comprehensive news research methodology:
@@ -148,6 +164,7 @@ tags: ["#daily-brief", "#news", "#strategic-intelligence"]
 interests: ["interest1", "interest2"]
 projects_referenced: ["project1"]
 items_count: [number]
+dedup_urls: ["https://primary-source-url-for-each-story-covered"]
 ---
 
 # Daily Brief - [Date]
PATCH

echo "Gold patch applied."
