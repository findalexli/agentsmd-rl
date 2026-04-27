#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "Zero config for 8 channels. Use when user asks to search, read, or interact" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -1,24 +1,16 @@
 ---
 name: agent-reach
 description: >
-  Give your AI agent eyes to see the entire internet. 7500+ GitHub stars.
+  Give your AI agent eyes to see the entire internet.
   Search and read 16 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
-  XiaoHongShu (小红书), Douyin (抖音), Weibo (微博), WeChat Articles (微信公众号),
-  Xiaoyuzhou Podcast (小宇宙播客), LinkedIn, Instagram, V2EX, RSS, Exa web search, and any web page.
-  One command install, zero config for 8 channels, agent-reach doctor for diagnostics.
-  Use when: (1) user asks to search or read any of these platforms,
-  (2) user shares a URL from any supported platform,
-  (3) user asks to search the web, find information online, or research a topic,
-  (4) user asks to post, comment, or interact on supported platforms,
-  (5) user asks to configure or set up a platform channel.
-  Triggers: "搜推特", "搜小红书", "看视频", "搜一下", "上网搜", "帮我查", "全网搜索",
-  "search twitter", "read tweet", "youtube transcript", "search reddit",
-  "read this link", "看这个链接", "B站", "bilibili", "抖音视频",
-  "微信文章", "公众号", "LinkedIn", "GitHub issue", "RSS", "微博",
-  "V2EX", "v2ex", "节点", "看主题", "技术社区",
-  "小宇宙", "xiaoyuzhou", "播客", "podcast", "转录", "transcribe",
-  "search online", "web search", "find information", "research",
-  "帮我配", "configure twitter", "configure proxy", "帮我安装".
+  XiaoHongShu, Douyin, Weibo, WeChat Articles, Xiaoyuzhou Podcast, LinkedIn,
+  Instagram, V2EX, RSS, Exa web search, and any web page.
+  Zero config for 8 channels. Use when user asks to search, read, or interact
+  on any supported platform, shares a URL, or asks to search the web.
+  Triggers: "搜推特", "搜小红书", "看视频", "搜一下", "上网搜", "帮我查",
+  "search twitter", "youtube transcript", "search reddit", "read this link",
+  "B站", "bilibili", "抖音视频", "微信文章", "公众号", "微博", "V2EX",
+  "小宇宙", "播客", "podcast", "web search", "research", "帮我安装".
 metadata:
   openclaw:
     homepage: https://github.com/Panniantong/Agent-Reach
PATCH

echo "Gold patch applied."
