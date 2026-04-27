#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "- \u82f1\u6587\uff1a`create pr`\u3001`create a pr`\u3001`open pr`\u3001`open a pr`\u3001`submit pr`\u3001`send pr`\u3001`draf" ".agents/skills/create-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-pr/SKILL.md b/.agents/skills/create-pr/SKILL.md
@@ -24,6 +24,12 @@ description: Create pull requests for ant-design using the repository's official
 - 总结当前分支改动用于提 PR
 - 用 `gh pr create` 为 `ant-design` 开 PR
 
+如果用户只输入很短的口语化指令，也应直接触发本 skill，不要因为信息太少而跳过。例如：
+- 中文：`创建pr`、`创建 PR`、`开pr`、`开个pr`、`提pr`、`提个pr`、`帮我提个pr`、`发pr`、`写pr`、`准备pr`。
+- 英文：`create pr`、`create a pr`、`open pr`、`open a pr`、`submit pr`、`send pr`、`draft pr`、`prepare pr`、`help me create a pr`、`open a pull request`。
+
+这类短句默认表示：先分析当前分支改动并整理待确认的 `base`、`title`、`body` 草稿，等用户确认后再真正创建 PR。
+
 ## 基本规则
 
 ### 一、必须以仓库模板为准
PATCH

echo "Gold patch applied."
