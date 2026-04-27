#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "One command install, zero config for 8 channels, agent-reach doctor for diagnost" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -1,9 +1,11 @@
 ---
 name: agent-reach
 description: >
-  Use the internet: search, read, and interact with 13+ platforms including
-  Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu (小红书), Douyin (抖音),
-  WeChat Articles (微信公众号), LinkedIn, RSS, Exa web search, and any web page.
+  Give your AI agent eyes to see the entire internet. 7500+ GitHub stars.
+  Search and read 14 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
+  XiaoHongShu (小红书), Douyin (抖音), Weibo (微博), WeChat Articles (微信公众号),
+  LinkedIn, Instagram, RSS, Exa web search, and any web page.
+  One command install, zero config for 8 channels, agent-reach doctor for diagnostics.
   Use when: (1) user asks to search or read any of these platforms,
   (2) user shares a URL from any supported platform,
   (3) user asks to search the web, find information online, or research a topic,
@@ -12,9 +14,12 @@ description: >
   Triggers: "搜推特", "搜小红书", "看视频", "搜一下", "上网搜", "帮我查", "全网搜索",
   "search twitter", "read tweet", "youtube transcript", "search reddit",
   "read this link", "看这个链接", "B站", "bilibili", "抖音视频",
-  "微信文章", "公众号", "LinkedIn", "GitHub issue", "RSS",
+  "微信文章", "公众号", "LinkedIn", "GitHub issue", "RSS", "微博",
   "search online", "web search", "find information", "research",
   "帮我配", "configure twitter", "configure proxy", "帮我安装".
+metadata:
+  openclaw:
+    homepage: https://github.com/Panniantong/Agent-Reach
 ---
 
 # Agent Reach — Usage Guide
PATCH

echo "Gold patch applied."
