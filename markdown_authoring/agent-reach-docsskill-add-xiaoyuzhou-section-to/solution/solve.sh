#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "~/.agent-reach/tools/xiaoyuzhou/transcribe.sh \"https://www.xiaoyuzhoufm.com/epis" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -2,9 +2,9 @@
 name: agent-reach
 description: >
   Give your AI agent eyes to see the entire internet. 7500+ GitHub stars.
-  Search and read 15 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
+  Search and read 16 platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
   XiaoHongShu (小红书), Douyin (抖音), Weibo (微博), WeChat Articles (微信公众号),
-  LinkedIn, Instagram, V2EX, RSS, Exa web search, and any web page.
+  Xiaoyuzhou Podcast (小宇宙播客), LinkedIn, Instagram, V2EX, RSS, Exa web search, and any web page.
   One command install, zero config for 8 channels, agent-reach doctor for diagnostics.
   Use when: (1) user asks to search or read any of these platforms,
   (2) user shares a URL from any supported platform,
@@ -16,6 +16,7 @@ description: >
   "read this link", "看这个链接", "B站", "bilibili", "抖音视频",
   "微信文章", "公众号", "LinkedIn", "GitHub issue", "RSS", "微博",
   "V2EX", "v2ex", "节点", "看主题", "技术社区",
+  "小宇宙", "xiaoyuzhou", "播客", "podcast", "转录", "transcribe",
   "search online", "web search", "find information", "research",
   "帮我配", "configure twitter", "configure proxy", "帮我安装".
 metadata:
@@ -133,6 +134,20 @@ cd ~/.agent-reach/tools/wechat-article-for-ai && python3 main.py "https://mp.wei
 
 > WeChat articles cannot be read with Jina Reader or curl. Must use Camoufox.
 
+## 小宇宙播客 / Xiaoyuzhou Podcast (groq-whisper + ffmpeg)
+
+```bash
+# 转录单集播客（输出文本到 /tmp/）
+~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
+```
+
+> 需要 ffmpeg + Groq API Key（免费）。  
+> 配置 Key：`agent-reach configure groq-key YOUR_KEY`  
+> 首次运行需安装工具：`agent-reach install --env=auto`  
+> 运行 `agent-reach doctor` 检查状态。  
+> 输出 Markdown 文件默认保存到 `/tmp/`。
+
+
 ## LinkedIn (mcporter)
 
 ```bash
PATCH

echo "Gold patch applied."
