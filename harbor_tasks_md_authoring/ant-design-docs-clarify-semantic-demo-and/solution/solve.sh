#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard
if grep -qF "- `components/**/demo/_semantic*.tsx` \u5c5e\u4e8e\u8bed\u4e49\u6587\u6863\u4e13\u7528 demo\uff0c\u662f\u4f8b\u5916\u573a\u666f\uff1a\u5141\u8bb8\u901a\u8fc7\u76f8\u5bf9\u8def\u5f84\u5f15\u7528 `.dumi/hook" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -35,11 +35,13 @@ ant-design/
 
 ## Demo 导入规范
 
-- 本规范同时适用于 `components/**/demo/` 和 `.dumi/` 下的示例、站点、主题相关文件。（`semantic.test.tsx` 文件除外）
-- 在这些目录下引入 Ant Design 组件、组件内部模块、工具方法、变量、类型定义时，一律使用绝对路径导入，不使用相对路径导入。
-- 允许的导入形式应优先使用项目公开入口或已配置别名，例如：`antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*`。
-- 禁止使用 `..`、`../xxx`、`../../xxx`、`./xxx` 这类相对路径去引用组件实现、内部模块、方法、变量、类型，包含跨 demo、跨目录复用的场景。
-- demo 与 `.dumi` 文件之间不要互相相对引用；如果需要复用少量逻辑，优先内联，或提取到可通过绝对路径访问的公共位置。
+- 常规 `components/**/demo/` 文件在引入 Ant Design 组件、组件内部模块、工具方法、变量、类型定义时，一律使用绝对路径导入，不使用相对路径导入。
+- `components/**/demo/_semantic*.tsx` 属于语义文档专用 demo，是例外场景：允许通过相对路径引用 `.dumi/hooks/useLocale`、`.dumi/theme/common/*` 等站点侧辅助模块。
+- `.dumi/` 目录内部的站点实现文件可按现有目录结构使用相对路径引用本目录模块；当引用仓库内 Ant Design 组件入口时，优先使用项目公开入口或已配置别名。
+- 允许的导入形式应优先使用项目公开入口或已配置别名，例如：`antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`@@/*`。
+- `.dumi/*` 不是仓库通用的 TS 路径别名；如需引用 `.dumi` 内部模块，请按文件位置使用相对路径。
+- 常规 demo 文件中，禁止使用 `..`、`../xxx`、`../../xxx`、`./xxx` 这类相对路径去引用组件实现、内部模块、方法、变量、类型，包含跨 demo、跨目录复用的场景。
+- 常规 demo 与 `.dumi` 文件之间不要互相相对引用（`_semantic*.tsx` 等站点语义 demo 复用 `.dumi` 辅助模块除外）。如果需要复用少量逻辑，优先内联，或提取到可通过绝对路径访问的公共位置。
 
 ## Test 导入规范
 
PATCH

echo "Gold patch applied."
