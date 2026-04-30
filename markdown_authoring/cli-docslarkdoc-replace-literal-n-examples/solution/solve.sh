#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "> **\u26a0\ufe0f `\\n` \u4e0d\u662f\u6362\u884c\uff1a** `--markdown \"...\\n...\"` \u91cc\u7684 `\\n` \u5728 shell \u91cc\u662f\u5b57\u9762\u53cd\u659c\u6760 + n\uff0c\u4f1a\u4f5c\u4e3a\u6587\u5b57\u5199\u5165\u6587" "skills/lark-doc/references/lark-doc-create.md" && grep -qF "> **\u26a0\ufe0f `\\n` \u4e0d\u662f\u6362\u884c\uff1a** `--markdown \"...\\n...\"` \u91cc\u7684 `\\n` \u5728 shell \u91cc\u662f\u5b57\u9762\u53cd\u659c\u6760 + n\uff0c\u4f1a\u4f5c\u4e3a\u6587\u5b57\u5199\u5165\u6587" "skills/lark-doc/references/lark-doc-update.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-doc/references/lark-doc-create.md b/skills/lark-doc/references/lark-doc-create.md
@@ -8,14 +8,22 @@
 ## 重要说明
 > **⚠️ 本文档中提到的 html 标签不需要在 Markdown 中转义！若转义，会导致相关的表格，多维表格，画板等 block 插入失败**
 
+> **⚠️ `\n` 不是换行：** `--markdown "...\n..."` 里的 `\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$'...\n...'`（bash/zsh）。示例见下方。
+
 ## 命令
 
 ```bash
 # 创建简单文档
-lark-cli docs +create --title "项目计划" --markdown "## 目标\n\n- 目标 1\n- 目标 2"
+lark-cli docs +create --title "项目计划" --markdown "## 目标
+
+- 目标 1
+- 目标 2"
 
 # 创建到指定文件夹
-lark-cli docs +create --title "会议纪要" --folder-token fldcnXXXX --markdown "## 讨论议题\n\n1. 进度\n2. 计划"
+lark-cli docs +create --title "会议纪要" --folder-token fldcnXXXX --markdown "## 讨论议题
+
+1. 进度
+2. 计划"
 
 # 创建到知识库节点下
 lark-cli docs +create --title "技术文档" --wiki-node wikcnXXXX --markdown "## API 说明"
@@ -25,6 +33,19 @@ lark-cli docs +create --title "概览" --wiki-space 7000000000000000000 --markdo
 
 # 创建到个人知识库
 lark-cli docs +create --title "学习笔记" --wiki-space my_library --markdown "## 笔记"
+
+# 从 stdin 读取（适合较长的 markdown 内容）
+lark-cli docs +create --title "长文档" --markdown - <<'MD'
+## 目标
+
+- 目标 1
+- 目标 2
+
+## 计划
+
+1. 第一步
+2. 第二步
+MD
 ```
 
 ## 返回值
@@ -116,13 +137,22 @@ wiki_space 可以从知识空间设置页面 URL 中获取，格式如：`https:
 ### 示例 1：创建简单文档
 
 ```bash
-lark-cli docs +create --title "项目计划" --markdown "## 项目概述\n\n这是一个新项目。\n\n## 目标\n\n- 目标 1\n- 目标 2"
+lark-cli docs +create --title "项目计划" --markdown "## 项目概述
+
+这是一个新项目。
+
+## 目标
+
+- 目标 1
+- 目标 2"
 ```
 
 ### 示例 2：使用飞书扩展语法
 
 ```bash
-lark-cli docs +create --title "产品需求" --markdown '<callout emoji="💡" background-color="light-blue">\n重要需求说明\n</callout>'
+lark-cli docs +create --title "产品需求" --markdown '<callout emoji="💡" background-color="light-blue">
+重要需求说明
+</callout>'
 ```
 
 # 内容格式
diff --git a/skills/lark-doc/references/lark-doc-update.md b/skills/lark-doc/references/lark-doc-update.md
@@ -8,17 +8,23 @@
 ## 重要说明
 > **⚠️ 本文档中提到的 html 标签不需要在 Markdown 中转义！若转义，会导致相关的表格，多维表格，画板等 block 插入失败**
 
+> **⚠️ `\n` 不是换行：** `--markdown "...\n..."` 里的 `\n` 在 shell 里是字面反斜杠 + n，会作为文字写入文档。请用真实换行：多行字符串、heredoc (`--markdown -`)、或 `$'...\n...'`（bash/zsh）。示例见下方。
+
 ## 命令
 
 ```bash
 # 追加内容
-lark-cli docs +update --doc "<doc_id_or_url>" --mode append --markdown "## 新章节\n\n追加内容"
+lark-cli docs +update --doc "<doc_id_or_url>" --mode append --markdown "## 新章节
+
+追加内容"
 
 # 定位替换（内容定位）
 lark-cli docs +update --doc "<doc_id>" --mode replace_range --selection-with-ellipsis "旧标题...旧结尾" --markdown "## 新内容"
 
 # 定位替换（标题定位）
-lark-cli docs +update --doc "<doc_id>" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明\n\n新内容"
+lark-cli docs +update --doc "<doc_id>" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明
+
+新内容"
 
 # 全文替换
 lark-cli docs +update --doc "<doc_id>" --mode replace_all --selection-with-ellipsis "张三" --markdown "李四"
@@ -38,7 +44,7 @@ lark-cli docs +update --doc "<doc_id>" --mode overwrite --markdown "# 全新内
 # 同时更新标题
 lark-cli docs +update --doc "<doc_id>" --mode append --markdown "## 更新日志" --new-title "文档 v2.0"
 
-# 在指定内容后新增两个空白画板
+# 在指定内容后新增两个空白画板（ANSI-C 引用，适合短标签序列）
 lark-cli docs +update --doc "<doc_id>" --mode insert_after --selection-with-ellipsis "有序列表" --markdown $'<whiteboard type="blank"></whiteboard>\n<whiteboard type="blank"></whiteboard>'
 ```
 
@@ -143,19 +149,25 @@ lark-cli docs +update --doc "<doc_id>" --mode insert_after --selection-with-elli
 ## append - 追加到末尾
 
 ```bash
-lark-cli docs +update --doc "文档ID或URL" --mode append --markdown "## 新章节\n\n追加的内容..."
+lark-cli docs +update --doc "文档ID或URL" --mode append --markdown "## 新章节
+
+追加的内容..."
 ```
 
 ## replace_range - 定位替换
 
 使用 `--selection-with-ellipsis`：
 ```bash
-lark-cli docs +update --doc "文档ID" --mode replace_range --selection-with-ellipsis "## 旧标题...旧结尾。" --markdown "## 新标题\n\n新的内容..."
+lark-cli docs +update --doc "文档ID" --mode replace_range --selection-with-ellipsis "## 旧标题...旧结尾。" --markdown "## 新标题
+
+新的内容..."
 ```
 
 使用 `--selection-by-title`（替换整个章节）：
 ```bash
-lark-cli docs +update --doc "文档ID" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明\n\n更新后的内容..."
+lark-cli docs +update --doc "文档ID" --mode replace_range --selection-by-title "## 功能说明" --markdown "## 功能说明
+
+更新后的内容..."
 ```
 
 ## replace_all - 全文替换
@@ -184,7 +196,9 @@ lark-cli docs +update --doc "文档ID" --mode delete_range --selection-by-title
 ⚠️ 会清空文档后重写，可能丢失图片、评论等，仅在需要完全重建文档时使用。
 
 ```bash
-lark-cli docs +update --doc "文档ID" --mode overwrite --markdown "# 新文档\n\n全新的内容..."
+lark-cli docs +update --doc "文档ID" --mode overwrite --markdown "# 新文档
+
+全新的内容..."
 ```
 
 ## 创建空白画板
PATCH

echo "Gold patch applied."
