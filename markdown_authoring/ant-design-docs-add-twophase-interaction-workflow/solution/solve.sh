#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "**\u5173\u952e\u539f\u5219\uff1a\u5148\u8349\u62df\u5b8c\u6574\u65b9\u6848\uff0c\u7b49\u7528\u6237\u8ba8\u8bba\u786e\u8ba4\u540e\u518d\u6267\u884c\u3002\u4e0d\u8981\u672a\u7ecf\u786e\u8ba4\u5c31\u56de\u590d\u6216\u5173\u95ed issue\u3002**" ".claude/skills/issue-reply/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/issue-reply/SKILL.md b/.claude/skills/issue-reply/SKILL.md
@@ -250,6 +250,34 @@ Issue 列表主要用于跟踪 **Bug 报告** 和 **功能请求**。
 
 ---
 
+## 交互流程
+
+当用户要求处理 issues 时，采用「先草拟、后确认」的两阶段流程：
+
+### 第一阶段：总览 + 草拟方案
+
+1. 使用 `gh issue list` 拉取指定范围的 open issues
+2. 对每个 issue 获取详情（body、comments、labels）
+3. 对每个 issue 给出处理方案，包括：
+   - 分类（Bug / Feature Request / 使用问题）
+   - 当前状态（无人回复 / 维护者已回复 / 等待用户反馈 等）
+   - 处理建议（需要回复 / 可以关闭 / 无需操作 / 等待中）
+   - 如果需要回复：草拟回复内容（含语言判断、正文、代码示例）
+   - 标签操作（添加/移除哪些标签）
+   - 是否关闭 issue
+4. 将所有方案一次性呈现给用户，**不要直接操作**
+
+### 第二阶段：讨论和确认
+
+1. 用户可以对任意 issue 的方案提出修改意见
+2. 根据反馈调整方案，直到用户满意
+3. 用户确认后执行操作（评论、加标签、关闭等）
+4. 如果用户说「就这样」或类似确认，直接执行
+
+**关键原则：先草拟完整方案，等用户讨论确认后再执行。不要未经确认就回复或关闭 issue。**
+
+---
+
 ## 参考资源
 
 详细标签列表和资源链接请参阅 `references/labels-and-resources.md`
PATCH

echo "Gold patch applied."
