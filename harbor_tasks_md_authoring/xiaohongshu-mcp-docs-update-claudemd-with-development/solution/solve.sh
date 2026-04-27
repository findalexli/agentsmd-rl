#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xiaohongshu-mcp

# Idempotency guard
if grep -qF "- \u6211\u9700\u8981: 1.\u672c\u5730 review; 2.\u8fdc\u7a0b PR review." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,2 +1,5 @@
 - 要求每次修改完后,需要帮我格式化 Go 源码文件.
-- 测试过程中产生的脚本和build中间文件,如果没有必要,则删除.
\ No newline at end of file
+- 测试过程中产生的脚本和build中间文件,如果没有必要,则删除.
+- 所有的feature变更,都需要使用分支进行开发.
+- 在我未同意之前, 你不能推送到远程.
+- 我需要: 1.本地 review; 2.远程 PR review.
\ No newline at end of file
PATCH

echo "Gold patch applied."
