#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency: skip if the distinctive new rule already exists
if grep -qF '可根据用户语言习惯决定使用中文或英文' CLAUDE.md; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index bda469d67c15..c2be766f4c17 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -37,10 +37,10 @@ ant-design/

 ### API 表格格式

-| Property | Description | Type | Default | Version |
-|---|---|---|---|---|
-| disabled | 是否禁用 | boolean | false | - |
-| type | 按钮类型 | `primary` \| `default` | `default` | - |
+| Property | Description | Type                   | Default   | Version |
+| -------- | ----------- | ---------------------- | --------- | ------- |
+| disabled | 是否禁用    | boolean                | false     | -       |
+| type     | 按钮类型    | `primary` \| `default` | `default` | -       |

 - 字符串默认值用反引号，布尔/数字直接写，无默认值用 `-`
 - API 按字母顺序排列，新增属性需声明版本号
@@ -65,7 +65,7 @@ ant-design/
 ### 标题与内容

 - PR 标题始终使用英文，格式：`类型: 简短描述`
-- PR 内容默认使用英文
+- PR 内容默认使用英文，可根据用户语言习惯决定使用中文或英文
 - 示例：`fix: fix button style issues in Safari browser`

 ### PR 模板（必须使用）
@@ -121,7 +121,7 @@ ant-design/
 #### 句式

 | 语言 | 格式 | 示例 |
-|---|---|---|
+| --- | --- | --- |
 | 中文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 修复 Button 在暗色主题下 \`color\` 的问题。` |
 | 英文 | `Emoji 动词 组件名 描述`（动词在前） | `🐞 Fix Button reversed \`hover\` colors in dark theme.` |

@@ -133,7 +133,7 @@ ant-design/
 ### Emoji 规范

 | Emoji  | 用途                   |
-|--------|------------------------|
+| ------ | ---------------------- |
 | 🐞     | 修复 Bug               |
 | 💄     | 样式更新或 token 更新  |
 | 🆕     | 新增特性 / 新增属性    |
PATCH

echo "Patch applied."
