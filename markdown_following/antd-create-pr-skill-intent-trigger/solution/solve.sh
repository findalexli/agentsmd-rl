#!/bin/bash
set -euo pipefail

cd /workspace/ant-design

SKILL_FILE=".agents/skills/create-pr/SKILL.md"

if grep -q '按意图触发，不按短语触发' "$SKILL_FILE"; then
  echo "Gold patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-pr/SKILL.md b/.agents/skills/create-pr/SKILL.md
index 3c4888f45eaa..a606e9d8f94a 100644
--- a/.agents/skills/create-pr/SKILL.md
+++ b/.agents/skills/create-pr/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: antd-create-pr
-description: Create pull requests for ant-design using the repository's official PR templates. Use when the user asks to create a PR, open a pull request, write PR title/body, summarize branch changes for a PR, or prepare an ant-design PR in Chinese or English. The skill must choose `.github/PULL_REQUEST_TEMPLATE_CN.md` or `.github/PULL_REQUEST_TEMPLATE.md` based on the user's language habit and keep the content aligned with ant-design's PR sections.
+description: Create pull requests for ant-design using the repository's official PR templates. Use this skill when the user asks to create/open a PR, draft PR title/body, summarize branch changes for a PR, or otherwise prepare PR content. Judge by intent rather than fixed phrases; short colloquial requests still count if they are about creating a PR rather than discussing PR concepts.
 ---
 
 # Ant Design PR 创建规范
@@ -15,24 +15,15 @@ description: Create pull requests for ant-design using the repository's official
 
 四、真正执行 `gh pr create` 之前，必须先把 `base`、`title`、`body` 给用户确认，确认后才能创建 PR。
 
-## 触发场景
-
-当用户提及以下任一情况时使用本 skill：
-
-- 创建 PR、发起 pull request
-- 写 PR 标题或 PR 描述
-- 总结当前分支改动用于提 PR
-- 用 `gh pr create` 为 `ant-design` 开 PR
+## 基本规则
 
-如果用户只输入很短的口语化指令，也应直接触发本 skill，不要因为信息太少而跳过。例如：
-- 中文：`创建pr`、`创建 PR`、`开pr`、`开个pr`、`提pr`、`提个pr`、`帮我提个pr`、`发pr`、`写pr`、`准备pr`。
-- 英文：`create pr`、`create a pr`、`open pr`、`open a pr`、`submit pr`、`send pr`、`draft pr`、`prepare pr`、`help me create a pr`、`open a pull request`。
+### 一、按意图触发，不按短语触发
 
-这类短句默认表示：先分析当前分支改动并整理待确认的 `base`、`title`、`body` 草稿，等用户确认后再真正创建 PR。
+只要能判断用户是在请求创建 PR，或为创建 PR 做准备，就应使用本 skill。
 
-## 基本规则
+不要把触发限制成固定说法。即使用户表达很短、很口语，或要求不完整，只要不是在单纯讨论 PR 概念，也应进入本 skill 的工作流。
 
-### 一、必须以仓库模板为准
+### 二、必须以仓库模板为准
 
 始终使用以下模板之一：
 
@@ -41,7 +32,7 @@ description: Create pull requests for ant-design using the repository's official
 
 不要自己改 section 名称，不要删掉模板里已有的主结构。可以删掉模板中的注释和说明性占位文本，但保留最终要提交的 section。
 
-### 二、模板语言由用户习惯决定，但标题固定英文
+### 三、模板语言由用户习惯决定，但标题固定英文
 
 按以下顺序判断：
 
@@ -58,7 +49,7 @@ description: Create pull requests for ant-design using the repository's official
 - `PR title` 要符合本文档的标题规范
 - `PR body` 才跟随模板语言
 
-### 三、先分析分支，再写 PR
+### 四、先分析分支，再写 PR
 
 创建 PR 前，必须先看：
 
@@ -69,7 +60,7 @@ description: Create pull requests for ant-design using the repository's official
 
 不要只根据工作区未提交内容写 PR，也不要只根据最近一个 commit 写 PR。
 
-### 四、先给草稿，后创建 PR
+### 五、先给草稿，后创建 PR
 
 无论用户是否说“直接帮我创建 PR”，都要先完成以下步骤：
 
@@ -80,14 +71,14 @@ description: Create pull requests for ant-design using the repository's official
 
 若用户中途要求修改标题、类型、changelog、目标分支等，应先更新草稿，再次确认。
 
-### 五、标题和正文要分工明确
+### 六、标题和正文要分工明确
 
 - PR 标题：用英文一句话概括本分支最主要的变动
 - PR 正文：说明背景、改法、关联 issue、更新日志影响
 
 正文不是逐文件流水账。要归纳“为什么改”和“改完后对开发者/用户有什么影响”。
 
-### 六、信息不足时不要硬写
+### 七、信息不足时不要硬写
 
 若以下内容缺失且无法从分支改动中可靠推断：
 
PATCH

echo "Solve applied."
