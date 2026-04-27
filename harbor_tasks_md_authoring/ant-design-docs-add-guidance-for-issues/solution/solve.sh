#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "- PR \u5df2\u5408\u5e76\u4f46\u65b0\u7248\u672c\u672a\u53d1\u5e03 \u2192 \u544a\u77e5\u7528\u6237\u7b49\u5f85\u65b0\u7248\u672c\u53d1\u5e03" ".claude/skills/issue-reply/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/issue-reply/SKILL.md b/.claude/skills/issue-reply/SKILL.md
@@ -107,6 +107,7 @@ Issue 列表主要用于跟踪 **Bug 报告** 和 **功能请求**。
 **首先检查版本：**
 
 - 老版本 + changelog 中已修复 → 引导用户升级验证
+- PR 已合并但新版本未发布 → 告知用户等待新版本发布
 
 **检查重现链接：**
 
@@ -194,33 +195,7 @@ Issue 列表主要用于跟踪 **Bug 报告** 和 **功能请求**。
 - 已解决
 - 用户长时间未回复（7天以上）
 
-**关闭时保持礼貌：**
-
-问题已解决（英文示例）：
-
-```
-Thanks for the feedback! This issue has been fixed in [version/PR#xxx].
-
-I'm closing this issue. Feel free to continue the discussion if you have further questions.
-```
-
-使用问题（中文示例）：
-
-```
-感谢反馈！经过分析，这是一个使用问题而非 bug。
-
-[解释解决方案]
-
-我将关闭此 issue。如果您仍有问题，欢迎继续讨论或重新打开。
-```
-
-用户长时间未回复（中文示例）：
-
-```
-由于长时间未收到回复，我将关闭此 issue。
-
-如果问题仍然存在，请提供更多信息后重新打开，或创建新的 issue。
-```
+**关闭时保持礼貌，简要说明关闭原因即可。**
 
 **不要关闭：**
 
PATCH

echo "Gold patch applied."
