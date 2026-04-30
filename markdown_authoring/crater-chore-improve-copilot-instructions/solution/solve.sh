#!/usr/bin/env bash
set -euo pipefail

cd /workspace/crater

# Idempotency guard
if grep -qF "- **\u6539\u8fdb\u5efa\u8bae\u4ee3\u7801**: \u5728\u7ed9\u51fa\u4fee\u6539\u5efa\u8bae\u4ee3\u7801\u65f6\uff0c\u8bf7\u6ce8\u610f\u53c2\u8003\u9879\u76ee\u5176\u5b83\u4ee3\u7801\u3001Workflow \u548c lint \u914d\u7f6e\uff0c\u5e76\u544a\u77e5\u7528\u6237\uff1a**\u76f4\u63a5\u5e94\u7528\u6765\u81ea Copilot \u7684" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -41,18 +41,12 @@
 - **分类标注**: 每条行内评论必须在开头明确标注该问题属于 **【核心规范】** 还是 **【优化建议】**。
 - **禁止重复评论**: 严禁对同一类重复出现的问题进行多处行内评论。例如：若文件内存在多处硬编码文本，仅在首处评论，并说明“该问题在文中多处出现，请开发者统一检查并修复”。
 - **保持评论精炼**: 评论应言简意赅。对于涉及范围广的复杂问题，避免在单个行内评论中堆砌过多内容或长段参考代码，重点在于指明方向。
-- **改进建议代码**: 仅在对解决方案有十足把握时提供 `Suggested Changes` 代码片段。若不确定，应引导开发者查阅文档、参考项目既有模式或咨询其他开发者。
+- **改进建议代码**: 在给出修改建议代码时，请注意参考项目其它代码、Workflow 和 lint 配置，并告知用户：**直接应用来自 Copilot 的修改可能导致 Workflow 失败，推荐参考评论本地修改并测试**。
 
 #### 总览评论 (Overview Comment)
 在撰写总览评论时：
 - **PR 描述校验与总结**: 评估开发者的 PR 描述是否涵盖了**变更意图、核心改动及测试验证**。若描述缺失或内容不全，应在总览评论中代为提供一份简短的变更总结，并明确提醒开发者补齐缺失项，引导其养成规范书写 PR 描述的习惯。
 - **质量评估**: 对 PR 的代码逻辑、测试完整性及架构契合度进行综合评价，重点肯定表现优异的亮点，而非机械地重复代码变更。
-- **统计摘要表**: 在总览评论中包含以下统计表格（重复问题按一类计为一条，总数应与行内评论数量一致）：
-
-  | 分类 | 数量 | 状态建议 |
-  | :--- | :--- | :--- |
-  | 核心规范 (MUST) | N | 建议修正阻断性问题后再行合入 |
-  | 优化建议 (SHOULD) | M | 供参考的改进方向 |
 - **寄语与建议**: 在评论最后，请用亲切且具激励性的语气肯定开发者为项目作出的贡献。基于本次 PR 的表现，给出一个简单的、有助于提升未来 PR 质量的小建议（如：关于 commit 拆分、测试覆盖度、或文档同步的意识等）。
 
 ---
PATCH

echo "Gold patch applied."
