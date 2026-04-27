#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "4. \u4e0d\u8981\u5728\u4ee3\u7801\u3001\u6ce8\u91ca\u3001\u6587\u6863\u3001\u63d0\u4ea4\u8bf4\u660e\u6216 PR \u63cf\u8ff0\u4e2d\u6cc4\u6f0f\u5185\u90e8\u8bc4\u6d4b\u6587\u4ef6\u540d\u6216\u4e0a\u4e0b\u6587\u8def\u5f84\uff08\u4f8b\u5982 `run-result.json`\u3001`run-trace.json`" "AGENTS.md" && grep -qF "- Do not leak internal evaluation filenames or context paths in code, comments, " "mcp/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -52,6 +52,16 @@ alwaysApply: true
 - tests 自动化测试
 </project_rules>
 
+<attribution_evaluation_guardrails>
+当任务来源于 failing eval、attribution issue、grader、benchmark、trace、result artifact 或其他评测证据时，必须额外遵守以下规则：
+1. 评测证据只用于定位问题，不等于产品公开契约；先判断是否存在真实用户可见的产品缺陷，再决定是否修改产品代码。
+2. 不要为了通过评测而新增 benchmark-only / grader-only 的兼容分支、提示词、注释、文案或行为。
+3. 不要新增同一语义字段的多套命名变体（例如大小写/下划线别名）来“兼容评测”，除非该别名已经是文档化的公开契约。
+4. 不要在代码、注释、文档、提交说明或 PR 描述中泄漏内部评测文件名或上下文路径（例如 `run-result.json`、`run-trace.json`、`evaluation-trace.json`、`.codebuddy/attribution-context`）；如必须提及，统一改写为“internal evaluation evidence”。
+5. 如果证据更像 grader / task contract 问题、仓库路由错误、或外部系统限制，而不是当前仓库里的真实产品缺陷，应停止产品表面改动，并在总结里明确说明原因与后续建议。
+6. 提交前必须自查 staged diff：确认没有评测专用措辞、没有内部 artifact 泄漏、没有为同一字段临时补多个别名。
+</attribution_evaluation_guardrails>
+
 <cloud_api_backend_rules>
 1. 如果需求涉及通过调用腾讯云 API 来实现后端功能，开始设计或编码前必须先查阅相关文档：
    - 云 API 文档：https://cloud.tencent.com/document/product/876/34809
@@ -61,13 +71,6 @@ alwaysApply: true
 4. 在实现前，需要根据文档确认接口能力、参数、鉴权方式、返回结构和限制条件，避免凭记忆实现。
 </cloud_api_backend_rules>
 
-<mcp_tool_design>
-1. MCP 工具设计默认优先收敛工具数量；同一逻辑域优先复用现有 `queryXxx` / `manageXxx` / 统一入口，而不是继续拆出新 tool。
-2. 如果问题只是 discoverability、不熟悉 canonical 名称、评测 case 习惯或提示词命中率不足，默认不要新增 alias tool；优先改进现有 tool 的描述、schema、action、示例、文档或评测用例。
-3. 只有当新 tool 带来独立能力边界、显著不同的参数形状 / 权限语义，或存在必须兼容的外部契约时，才考虑新增。
-4. 任何新增 tool 的方案都必须先回答：为什么不能并入现有入口；如果回答不充分，应视为坏味道并继续收敛设计。
-</mcp_tool_design>
-
 <add_aiide>
 # CloudBase AI Toolkit - 新增 AI IDE 支持工作流
 
@@ -113,9 +116,10 @@ cp -r doc/* {cloudbase-docs dir}/docs/ai/cloudbase-ai-toolkit/
 
 
 <git_push>
-提交代码注意 commit 采用 conventional-changelog 风格，在feat(xxx): 后面提加一个 emoji 字符，提交信息使用英文描述
-默认仅执行 `git push github`；不要再推荐或默认执行 `cnb` 相关推送，除非用户明确要求
-提交 PR 之后不要立刻结束，先等待几分钟，观察 review 评论和 CI 结果；如果有可执行的失败项或反馈，继续在同一分支修复并更新 PR
+提交代码注意 commit 采用 conventional-changelog 风格，在 `feat(xxx):` 后面加一个 emoji，提交信息使用英文描述。
+默认只推送 GitHub 远端，不要执行 `cnb` 推送，也不要使用 `--force`：
+- `git push github HEAD`
+提交 PR 之后不要立刻结束，先等待几分钟，观察 review 评论和 CI 结果；如果有可执行的失败项或反馈，继续在同一分支修复并更新 PR。
 </git_push>
 
 <workflow>
@@ -216,12 +220,11 @@ cp -r doc/* {cloudbase-docs dir}/docs/ai/cloudbase-ai-toolkit/
 
 
 <git_push>
-1. 提交代码注意 commit 采用 conventional-changelog 风格，在feat(xxx): 后面提加一个 emoji 字符，提交信息使用英文描述
-2. 提交代码不要直接提到 main，可以提一个分支，例如 feature/xxx，然后
-
-默认仅执行 `git push github`；不要再推荐或默认执行 `cnb` 相关推送，除非用户明确要求
-3. 然后自动创建 PR
-4. 创建 PR 后先等待几分钟，再检查 review 评论和 CI；如果有可执行的问题，继续在同一分支修复并更新 PR
+1. 提交代码注意 commit 采用 conventional-changelog 风格，在 `feat(xxx):` 后面加一个 emoji，提交信息使用英文描述。
+2. 提交代码不要直接推到 `main`，使用 feature 分支，并且默认只推送 GitHub 远端，不要执行 `cnb` 推送，也不要使用 `--force`：
+   - `git push github HEAD`
+3. 然后自动创建 PR。
+4. 创建 PR 后先等待几分钟，再检查 review 评论和 CI；如果有可执行的问题，继续在同一分支修复并更新 PR。
 </git_push>
 
 <skills_and_rules_maintenance>
diff --git a/mcp/AGENTS.md b/mcp/AGENTS.md
@@ -11,6 +11,17 @@ inclusion: always
 
 This file is a compatibility projection of the CloudBase routing contract. Keep its semantics aligned with the CloudBase source guideline, and express routing with stable skill identifiers rather than repo-specific file paths.
 
+### Attribution and evaluation guardrails
+
+When a task is triggered by failing evaluations, attribution issues, grader output, benchmark evidence, traces, or result artifacts, treat that evidence as diagnosis input rather than a public product contract.
+
+- Only change product behavior when you can explain a real user-visible defect in this repository.
+- Do not add benchmark-only or grader-only branches, wording, prompts, comments, or shims just to satisfy evaluation output.
+- Do not add multiple naming variants for the same semantic field unless the alias is already part of a documented public contract.
+- Do not leak internal evaluation filenames or context paths in code, comments, docs, commit messages, or PR bodies, including `run-result.json`, `run-trace.json`, `evaluation-trace.json`, and `.codebuddy/attribution-context`; rewrite them as “internal evaluation evidence” when needed.
+- If the evidence points to a grader mismatch, task-contract mismatch, wrong-repo routing, or external limitation rather than a real product defect here, stop product-surface edits and explain that in the summary.
+- Before commit, review the staged diff specifically for evaluator-only wording, internal artifact leakage, and temporary alias-field additions.
+
 ### Global must-read rules
 
 - Identify the scenario first. Do not start implementation before reading the matching rule file.
PATCH

echo "Gold patch applied."
