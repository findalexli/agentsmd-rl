#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-reach

# Idempotency guard
if grep -qF "mcporter call 'xiaohongshu.publish_with_video(title: \"\u6807\u9898\", content: \"\u6b63\u6587\", video:" "agent_reach/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/agent_reach/skill/SKILL.md b/agent_reach/skill/SKILL.md
@@ -145,20 +145,27 @@ Note: On servers, Reddit may block your IP. Use proxy or search via Exa instead.
 
 ### 小红书 / XiaoHongShu (mcporter + xiaohongshu-mcp)
 
+> ⚠️ 需要登录。使用 Cookie-Editor 导入 cookies 或扫码登录。
+
 ```bash
-# Search notes
+# 搜索笔记
 mcporter call 'xiaohongshu.search_feeds(keyword: "query")'
 
-# Read a note
+# 获取笔记详情（含评论）
 mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy")'
 
-# Get comments
-mcporter call 'xiaohongshu.get_feed_comments(feed_id: "xxx", xsec_token: "yyy")'
+# 获取全部评论
+mcporter call 'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy", load_all_comments: true)'
+
+# 发布图文笔记
+mcporter call 'xiaohongshu.publish_content(title: "标题", content: "正文", images: ["/path/to/img.jpg"], tags: ["美食"])'
 
-# Post a note
-mcporter call 'xiaohongshu.create_image_feed(title: "标题", desc: "内容", image_paths: ["/path/to/img.jpg"])'
+# 发布视频笔记
+mcporter call 'xiaohongshu.publish_with_video(title: "标题", content: "正文", video: "/path/to/video.mp4", tags: ["vlog"])'
 ```
 
+其他功能（点赞、收藏、评论、用户主页等）：`npx mcporter list xiaohongshu`
+
 ### 抖音 / Douyin (mcporter + douyin-mcp-server)
 
 ```bash
PATCH

echo "Gold patch applied."
