#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xiaohongshu-mcp

# Idempotency guard
if grep -qF "- \u91cd\u70b9\uff1aPR \u4ee3\u7801\u4e2d\u5982\u679c\u51fa\u73b0\u5927\u91cf\u7684 JS \u6ce8\u5165\u7684\u884c\u4e3a\uff0c\u8981\u68c0\u67e5\u4e00\u4e0b\u662f\u5426\u662f\u5fc5\u987b\u7684\uff0c\u5982\u679c\u53ef\u4ee5\u7528 Go \u7684 go-rod \u66ff\u4ee3\u7684\u8bdd\uff0c\u5219\u76f4\u63a5\u8bc4\u8bba\u9700\u8981\u7528 go-rod \u884c" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,7 +1,15 @@
+# Project Guidelines
+
+##  本地开发规范
+
 - 要求每次修改完后,需要帮我格式化 Go 源码文件.
 - 测试过程中产生的脚本和build中间文件,如果没有必要,则删除.
 - 所有的feature变更,都需要使用分支进行开发.
 - 在我未同意之前, 你不能推送到远程.
 - 我需要: 1.本地 review; 2.远程 PR review.
 - 不要过度设计, 保持代码的简洁和易读.
-- 使用中文注释，一定要简洁明了.专业名词可以用英文.
\ No newline at end of file
+- 使用中文注释，一定要简洁明了.专业名词可以用英文.
+
+## PR Review 重点
+
+- 重点：PR 代码中如果出现大量的 JS 注入的行为，要检查一下是否是必须的，如果可以用 Go 的 go-rod 替代的话，则直接评论需要用 go-rod 行为替代。
PATCH

echo "Gold patch applied."
