#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pro-components

# Idempotency guard
if grep -qF "- **API \u5c5e\u6027\u6392\u5e8f\u89c4\u5219\uff1a\u4f7f\u7528\u62fc\u97f3\u6392\u5e8f\uff08Pinyin Ranking\uff09**" ".cursor/rules/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/AGENTS.md b/.cursor/rules/AGENTS.md
@@ -15,24 +15,22 @@
 ### 开发环境要求
 
 - Node.js 版本 >= 16
-- 推荐使用 npm 或 yarn
+- **包管理工具：使用 pnpm**
 - Chrome 80+ 浏览器兼容性
 
 ### 安装依赖
 
 ```bash
-npm install
-# 或
-yarn install
+pnpm install
 ```
 
 ### 开发命令
 
 ```bash
-npm start     # 启动开发服务器
-npm run build # 构建项目
-npm test      # 运行测试
-npm run lint  # 代码检查
+pnpm start     # 启动开发服务器
+pnpm run build # 构建项目
+pnpm test      # 运行测试
+pnpm run lint  # 代码检查
 ```
 
 ## 代码风格指南
@@ -112,7 +110,11 @@ ComponentRef {
 - 函数类型使用箭头函数表达式
 - 无默认值使用 `-`
 - 描述首字母大写，结尾无句号
-- API 按字母顺序排列
+- **API 属性排序规则：使用拼音排序（Pinyin Ranking）**
+  - 所有 API 属性必须按照属性名的拼音顺序排列
+  - 英文属性按照字母顺序排列
+  - 中文属性按照拼音顺序排列
+  - 这确保了文档的一致性和可读性
 
 ## TypeScript 规范
 
PATCH

echo "Gold patch applied."
