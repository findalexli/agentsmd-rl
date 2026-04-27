#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "agent-reach/SKILL.md" "agent-reach/SKILL.md" && grep -qF "agent_reach/integrations/skill/SKILL.md" "agent_reach/integrations/skill/SKILL.md" && grep -qF "- **Paste cookies:** User installs [Cookie-Editor](https://chromewebstore.google" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent-reach/SKILL.md b/agent-reach/SKILL.md
@@ -1,87 +0,0 @@
----
-name: agent-reach
-description: >
-  Give your AI agent eyes to see the entire internet. Read and search across
-  Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, RSS, and any web page
-  — all from a single CLI. Use when: (1) reading content from URLs (tweets, Reddit posts,
-  articles, videos), (2) searching across platforms (web, Twitter, Reddit, GitHub, YouTube,
-  Bilibili, XiaoHongShu), (3) checking channel health or updating Agent Reach.
-  Triggers: "search Twitter/Reddit/YouTube", "read this URL", "find posts about",
-  "搜索", "读取", "查一下", "看看这个链接".
----
-
-# Agent Reach
-
-Read and search the internet across 9+ platforms via unified CLI.
-
-## Setup
-
-First check if agent-reach is installed:
-```bash
-agent-reach doctor
-```
-
-If command not found, install it:
-```bash
-pip install https://github.com/Panniantong/agent-reach/archive/main.zip
-agent-reach install --env=auto
-```
-
-`install` auto-detects your environment and installs all dependencies (Node.js, mcporter, bird CLI, gh CLI). Read the output and run `agent-reach doctor` to see what's active.
-
-For channels that need user input, ask the user. See the full setup guide:
-https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
-
-## Commands
-
-### Read any URL
-```bash
-agent-reach read <url>
-agent-reach read <url> --json    # structured output
-```
-Handles: tweets, Reddit posts, articles, YouTube (transcripts), GitHub repos, etc.
-
-### Search
-
-```bash
-agent-reach search "query"             # web search (Exa)
-agent-reach search-twitter "query"     # Twitter/X
-agent-reach search-reddit "query"      # Reddit (--sub <subreddit>)
-agent-reach search-github "query"      # GitHub (--lang <language>)
-agent-reach search-youtube "query"     # YouTube
-agent-reach search-bilibili "query"    # Bilibili (B站)
-agent-reach search-xhs "query"        # XiaoHongShu (小红书)
-```
-
-All search commands support `-n <count>` for number of results.
-
-### Management
-
-```bash
-agent-reach doctor        # channel status overview
-agent-reach watch         # quick health + update check (for scheduled tasks)
-agent-reach check-update  # check for new versions
-```
-
-### Configure channels
-
-```bash
-agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
-agent-reach configure proxy http://user:pass@ip:port
-agent-reach configure --from-browser chrome    # auto-extract cookies
-```
-
-## Channel Status Tiers
-
-- **Tier 0 (zero config):** Web, YouTube, RSS, Twitter (read-only via Jina)
-- **Tier 1 (free setup):** Exa web search (mcporter required)
-- **Tier 2 (user config):** Twitter search (cookie), Reddit full (proxy), GitHub (token), Bilibili (proxy), XiaoHongShu (MCP)
-
-Run `agent-reach doctor` to see which channels are active.
-
-## Tips
-
-- Always try `agent-reach read <url>` first for any URL — it auto-detects the platform
-- For Twitter cookies, recommend the user install [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension
-- Reddit and Bilibili block server IPs — suggest a residential proxy (~$1/month) if on a server
-- If a channel breaks, run `agent-reach doctor` to diagnose
diff --git a/agent_reach/integrations/skill/SKILL.md b/agent_reach/integrations/skill/SKILL.md
@@ -1,65 +0,0 @@
----
-name: agent-reach
-description: "Give your AI Agent eyes to see the entire internet. Search + read 10+ platforms with one install."
-install: pip install git+https://github.com/Panniantong/agent-reach.git
----
-
-# Agent Reach — 给 Agent 装上眼睛 👁️
-
-安装后你就能搜索和阅读全网内容。
-
-## 安装
-
-```bash
-pip install git+https://github.com/Panniantong/agent-reach.git
-```
-
-## 装完直接能用的（零配置）
-
-- `agent-reach read <URL>` — 读取任意网页、GitHub、B站、YouTube、RSS
-- `agent-reach search-github "query"` — 搜索 GitHub 仓库
-- `agent-reach doctor` — 查看所有平台状态
-
-## 解锁更多功能
-
-运行 `agent-reach configure` 进行交互式配置，或者读取以下指南：
-
-| 功能 | 指南文件 |
-|------|---------|
-| 全网搜索 + Reddit搜索 + Twitter搜索 | `agent_reach/guides/setup-exa.md` |
-| Reddit 完整阅读 | `agent_reach/guides/setup-reddit.md` |
-| Twitter 高级（时间线/线程） | `agent_reach/guides/setup-twitter.md` |
-| 小红书 | `agent_reach/guides/setup-xiaohongshu.md` |
-| 微信公众号 | `agent_reach/guides/setup-wechat.md` |
-| 视频语音转文字 | `agent_reach/guides/setup-groq.md` |
-
-每个指南里有详细的步骤说明，你（Agent）可以照着做，只有需要人类操作的部分（登录、复制 key）才需要问用户。
-
-## MCP Server
-
-如果你的 Agent 平台支持 MCP：
-
-```bash
-pip install agent-reach[mcp]
-python -m agent_reach.integrations.mcp_server
-```
-
-提供 8 个工具：read_url, read_batch, detect_platform, search, search_reddit, search_github, search_twitter, get_status
-
-## Python API
-
-```python
-from agent_reach import AgentReach
-import asyncio
-
-eyes = AgentReach()
-
-# 读取
-result = asyncio.run(eyes.read("https://github.com/openai/gpt-4"))
-
-# 搜索
-results = asyncio.run(eyes.search("AI agent framework"))
-
-# 健康检查
-print(eyes.doctor_report())
-```
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -2,17 +2,21 @@
 name: agent-reach
 description: >
   Give your AI agent eyes to see the entire internet. Read and search across
-  Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, RSS, and any web page
-  — all from a single CLI. Use when: (1) reading content from URLs (tweets, Reddit posts,
-  articles, videos), (2) searching across platforms (web, Twitter, Reddit, GitHub, YouTube,
-  Bilibili, XiaoHongShu), (3) checking channel health or updating Agent Reach.
+  Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, Instagram, LinkedIn,
+  Boss直聘, RSS, and any web page — all from a single CLI.
+  Use when: (1) reading content from URLs (tweets, Reddit posts, articles, videos),
+  (2) searching across platforms (web, Twitter, Reddit, GitHub, YouTube, Bilibili,
+  XiaoHongShu, Instagram, LinkedIn, Boss直聘),
+  (3) user asks to configure/enable a platform channel,
+  (4) checking channel health or updating Agent Reach.
   Triggers: "search Twitter/Reddit/YouTube", "read this URL", "find posts about",
-  "搜索", "读取", "查一下", "看看这个链接".
+  "搜索", "读取", "查一下", "看看这个链接",
+  "帮我配", "帮我添加", "帮我安装".
 ---
 
 # Agent Reach
 
-Read and search the internet across 9+ platforms via unified CLI.
+Read and search the internet across 12+ platforms via unified CLI.
 
 ## Setup
 
@@ -27,10 +31,7 @@ pip install https://github.com/Panniantong/agent-reach/archive/main.zip
 agent-reach install --env=auto
 ```
 
-`install` auto-detects your environment and installs all dependencies (Node.js, mcporter, bird CLI, gh CLI). Read the output and run `agent-reach doctor` to see what's active.
-
-For channels that need user input, ask the user. See the full setup guide:
-https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
+`install` auto-detects your environment and installs core dependencies (Node.js, mcporter, bird CLI, gh CLI, instaloader). Read the output and run `agent-reach doctor` to see what's active.
 
 ## Commands
 
@@ -39,7 +40,7 @@ https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
 agent-reach read <url>
 agent-reach read <url> --json    # structured output
 ```
-Handles: tweets, Reddit posts, articles, YouTube (transcripts), GitHub repos, etc.
+Handles: tweets, Reddit posts, articles, YouTube/Bilibili (transcripts), GitHub repos, Instagram posts, LinkedIn profiles, Boss直聘 jobs, XiaoHongShu notes, RSS feeds, and any web page.
 
 ### Search
 
@@ -51,6 +52,9 @@ agent-reach search-github "query"      # GitHub (--lang <language>)
 agent-reach search-youtube "query"     # YouTube
 agent-reach search-bilibili "query"    # Bilibili (B站)
 agent-reach search-xhs "query"        # XiaoHongShu (小红书)
+agent-reach search-instagram "query"   # Instagram
+agent-reach search-linkedin "query"    # LinkedIn
+agent-reach search-bosszhipin "query"  # Boss直聘
 ```
 
 All search commands support `-n <count>` for number of results.
@@ -67,21 +71,35 @@ agent-reach check-update  # check for new versions
 
 ```bash
 agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
+agent-reach configure instagram-cookies "sessionid=xxx; csrftoken=yyy; ..."
 agent-reach configure proxy http://user:pass@ip:port
-agent-reach configure --from-browser chrome    # auto-extract cookies
+agent-reach configure --from-browser chrome    # auto-extract cookies from local browser
 ```
 
-## Channel Status Tiers
+## Configuring a channel ("帮我配 XXX")
+
+All channels follow the same flow. When a user asks to configure/enable any channel:
+
+1. Run `agent-reach doctor`
+2. Find the channel in the output — it shows the current status (✅/⚠️/⬜) and **what to do next**
+3. Execute whatever you can automatically (install packages, start services, register MCP)
+4. For steps that require human action (scan QR code, paste cookies, login), tell the user exactly what to do
+5. After the user completes their part, run `agent-reach doctor` again to verify
+
+**Do NOT memorize per-channel steps.** Always rely on `doctor` output — it stays up-to-date even when backends change.
+
+### Common human actions
 
-- **Tier 0 (zero config):** Web, YouTube, RSS, Twitter (read-only via Jina)
-- **Tier 1 (free setup):** Exa web search (mcporter required)
-- **Tier 2 (user config):** Twitter search (cookie), Reddit full (proxy), GitHub (token), Bilibili (proxy), XiaoHongShu (MCP)
+These are things only the user can do. When `doctor` indicates one is needed, explain it clearly:
 
-Run `agent-reach doctor` to see which channels are active.
+- **Paste cookies:** User installs [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension → goes to the website → exports Header String → sends it to you → you run `agent-reach configure <platform>-cookies "..."`
+- **Scan QR code:** User opens the URL shown in `doctor` output on their phone/browser and scans with the platform's app
+- **Browser login:** Some MCP services need a one-time browser login; on servers without a display, user may need VNC
+- **Proxy:** Reddit/Bilibili/XiaoHongShu block server IPs — suggest a residential proxy (~$1/month) if on a server
 
 ## Tips
 
 - Always try `agent-reach read <url>` first for any URL — it auto-detects the platform
-- For Twitter cookies, recommend the user install [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) Chrome extension
-- Reddit and Bilibili block server IPs — suggest a residential proxy (~$1/month) if on a server
+- If a channel is ⬜ but the user hasn't asked for it, don't push — let them opt in
 - If a channel breaks, run `agent-reach doctor` to diagnose
+- LinkedIn and Boss直聘 have Jina Reader fallback even without full setup
PATCH

echo "Gold patch applied."
