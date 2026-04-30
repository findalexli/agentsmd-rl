#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xint

# Idempotency guard
if grep -qF "Supports search, watch, trends, bookmarks, likes/following (OAuth), Grok analysi" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,20 +1,12 @@
 ---
 name: xint
 description: >
-  X Intelligence CLI — search, analyze, and engage on X/Twitter from the terminal.
-  Use when: (1) user says "x research", "search x for", "search twitter for",
-  "what are people saying about", "what's twitter saying", "check x for", "x search",
-  "search x", "find tweets about", "monitor x for", "track followers", (2) user is working on
-  something where recent X discourse would provide useful context (new library releases,
-  API changes, product launches, cultural events, industry drama), (3) user wants to find
-  what devs/experts/community thinks about a topic, (4) user needs real-time monitoring ("watch"),
-  (5) user wants AI-powered analysis ("analyze", "sentiment", "report"),
-  (6) user wants to sync bookmarks to Obsidian ("sync bookmarks", "capture bookmarks",
-  "bookmark research", "save my bookmarks to obsidian").
-  Also supports: bookmarks, likes, following (read/write), trending topics, Grok AI analysis,
-  and cost tracking. Export as JSON, JSONL (pipeable), CSV, or Markdown.
-  Non-goals: Not for posting tweets, not for DMs, not for enterprise features.
-  Requires OAuth for user-context operations (bookmarks, likes, following, diff).
+  X Intelligence CLI for searching, monitoring, and analyzing X/Twitter from the terminal.
+  Use for X/Twitter research prompts such as "search x", "find tweets about", "what's X saying",
+  trend checks, follower diffs, real-time watch tasks, sentiment/report analysis, and bookmark-sync workflows.
+  Best when recent community discourse matters (library/API changes, launches, market or cultural events).
+  Supports search, watch, trends, bookmarks, likes/following (OAuth), Grok analysis, and JSON/JSONL/CSV/Markdown export.
+  Non-goals: posting original tweets, DMs, or enterprise-only features.
 credentials:
   - name: X_BEARER_TOKEN
     description: X API v2 bearer token for search, profile, thread, tweet, trends
PATCH

echo "Gold patch applied."
