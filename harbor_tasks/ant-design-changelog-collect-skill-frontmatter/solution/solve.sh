#!/bin/bash
set -euo pipefail

cd /workspace/ant-design

SKILL_FILE=".agents/skills/changelog-collect/SKILL.md"

# Idempotency: if frontmatter is already present, do nothing.
if head -n 1 "$SKILL_FILE" | grep -q '^---$' && grep -q '^name: changelog-collect$' "$SKILL_FILE"; then
    echo "Frontmatter already present. Nothing to do."
    exit 0
fi

# Apply gold patch as a HEREDOC.
git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/changelog-collect/SKILL.md b/.agents/skills/changelog-collect/SKILL.md
index 4069948b5728..99bbb9e9a5a7 100644
--- a/.agents/skills/changelog-collect/SKILL.md
+++ b/.agents/skills/changelog-collect/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: changelog-collect
+description: 收集 ant-design 两个版本之间的 PR 信息并整理 changelog 草稿，更新到 CHANGELOG.zh-CN.md 和 CHANGELOG.en-US.md 时使用。适用于收集 changelog、生成 changelog、更新 changelog、版本对比等场景。
+---
+
 # Changelog 收集工具

 ## 目标
PATCH

echo "Patch applied."
