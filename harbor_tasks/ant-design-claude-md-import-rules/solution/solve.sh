#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ant-design

# Idempotency guard: if the new sections are already present, skip.
if grep -q '^## Demo 导入规范$' CLAUDE.md && grep -q '^## Test 导入规范$' CLAUDE.md; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index c2be766f4c17..0bfe58a9c884 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -33,6 +33,24 @@ ant-design/

 ---

+## Demo 导入规范
+
+- 本规范同时适用于 `components/**/demo/` 和 `.dumi/` 下的示例、站点、主题相关文件。（`semantic.test.tsx` 文件除外）
+- 在这些目录下引入 Ant Design 组件、组件内部模块、工具方法、变量、类型定义时，一律使用绝对路径导入，不使用相对路径导入。
+- 允许的导入形式应优先使用项目公开入口或已配置别名，例如：`antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*`。
+- 禁止使用 `..`、`../xxx`、`../../xxx`、`./xxx` 这类相对路径去引用组件实现、内部模块、方法、变量、类型，包含跨 demo、跨目录复用的场景。
+- demo 与 `.dumi` 文件之间不要互相相对引用；如果需要复用少量逻辑，优先内联，或提取到可通过绝对路径访问的公共位置。
+
+## Test 导入规范
+
+- 本规范适用于 `components/**/__tests__/` 下的测试文件。
+- 在这些目录下引入 Ant Design 组件，或引入组件内部模块、工具方法、变量、类型定义时，一律使用相对路径导入，不使用绝对路径导入。
+- 测试文件应优先从当前组件目录、相邻内部模块或共享测试工具目录通过相对路径引用，例如：`..`、`../index`、`../xxx`、`../../_util/*`、`../../../tests/shared/*`。
+- 禁止在 `__tests__` 目录下使用 `antd`、`antd/es/*`、`antd/lib/*`、`antd/locale/*`、`.dumi/*`、`@@/*` 这类绝对路径或别名路径去引用仓库内代码。
+- 如需引用仓库外第三方依赖，仍按依赖包名正常导入，例如 `react`、`@testing-library/react`、`dayjs`。
+
+---
+
 ## 文档规范

 ### API 表格格式
PATCH

echo "Gold patch applied."
