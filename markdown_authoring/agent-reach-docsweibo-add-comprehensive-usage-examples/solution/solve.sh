#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "> Zero config. No login needed. Uses mobile API with auto visitor cookies." "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -126,6 +126,42 @@ cd ~/.agent-reach/tools/wechat-article-for-ai && python3 main.py "https://mp.wei
 
 > WeChat articles cannot be read with Jina Reader or curl. Must use Camoufox.
 
+## 微博 / Weibo (mcporter)
+
+```bash
+# 热搜榜
+mcporter call 'weibo.get_trendings(limit: 20)'
+
+# 搜索用户
+mcporter call 'weibo.search_users(keyword: "雷军", limit: 10)'
+
+# 获取用户资料
+mcporter call 'weibo.get_profile(uid: "1195230310")'
+
+# 获取用户微博动态
+mcporter call 'weibo.get_feeds(uid: "1195230310", limit: 20)'
+
+# 获取用户热门微博
+mcporter call 'weibo.get_hot_feeds(uid: "1195230310", limit: 10)'
+
+# 搜索微博内容
+mcporter call 'weibo.search_content(keyword: "人工智能", limit: 20)'
+
+# 搜索话题
+mcporter call 'weibo.search_topics(keyword: "AI", limit: 10)'
+
+# 获取微博评论
+mcporter call 'weibo.get_comments(mid: "5099916367123456", limit: 50)'
+
+# 获取粉丝列表
+mcporter call 'weibo.get_fans(uid: "1195230310", limit: 20)'
+
+# 获取关注列表
+mcporter call 'weibo.get_followers(uid: "1195230310", limit: 20)'
+```
+
+> Zero config. No login needed. Uses mobile API with auto visitor cookies.
+
 ## 小宇宙播客 / Xiaoyuzhou Podcast (groq-whisper + ffmpeg)
 
 ```bash
PATCH

echo "Gold patch applied."
