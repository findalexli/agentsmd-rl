#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.9 -i <\u4ea7\u7269\u6587\u4ef6> --to openapi --format json \\" "skills/lark-whiteboard/SKILL.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.9 -i <DSL \u6587\u4ef6> --to openapi --format json -" "skills/lark-whiteboard/references/lark-whiteboard-update.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords." "skills/lark-whiteboard/references/layout.md" && grep -qF "name: string;                 // \u56fe\u6807\u540d\u79f0\uff0c\u4ece npx -y @larksuite/whiteboard-cli@^0.2.9 " "skills/lark-whiteboard/references/schema.md" && grep -qF "- \u6e32\u67d3 PNG\uff08\u4ec5\u7528\u4e8e\u9884\u89c8\u9a8c\u8bc1\uff0c\u4e0d\u662f\u6700\u7ec8\u4ea7\u7269\uff09\uff1anpx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json" "skills/lark-whiteboard/routes/dsl.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd --to openapi --format jso" "skills/lark-whiteboard/routes/mermaid.md" && grep -qF "\u5bfc\u51fa     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --to " "skills/lark-whiteboard/routes/svg.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1a\u7528 .cjs \u811a\u672c\u8ba1\u7b97\u67f1\u4f53\u4f4d\u7f6e\u548c\u9ad8\u5ea6\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteboar" "skills/lark-whiteboard/scenes/bar-chart.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u5fc5\u987b\uff09\uff1a\u7528 .cjs \u811a\u672c\u901a\u8fc7\u4e09\u89d2\u51fd\u6570\u8ba1\u7b97\u9c7c\u9aa8\u5750\u6807\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteb" "skills/lark-whiteboard/scenes/fishbone.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u5fc5\u987b\uff09\uff1a\u7528 .cjs \u811a\u672c\u6781\u5750\u6807\u8ba1\u7b97\u9636\u6bb5\u6807\u7b7e\u4f4d\u7f6e\u3001SVG \u5706\u73af\u5207\u5272\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuit" "skills/lark-whiteboard/scenes/flywheel.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1a\u7528 .cjs \u811a\u672c\u8ba1\u7b97\u6570\u636e\u70b9\u5750\u6807\u548c\u6298\u7ebf\u8def\u5f84\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteb" "skills/lark-whiteboard/scenes/line-chart.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1aTreemap \u9700\u8981\u7cbe\u786e\u7684\u9762\u79ef\u6bd4\u4f8b\u8ba1\u7b97\uff0c\u7528 .cjs \u811a\u672c\u9012\u5f52\u5207\u5206\u77e9\u5f62\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @la" "skills/lark-whiteboard/scenes/treemap.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-whiteboard/SKILL.md b/skills/lark-whiteboard/SKILL.md
@@ -12,10 +12,8 @@ metadata:
 ---
 
 > [!IMPORTANT]
-> **执行前检查环境**：
-> - 运行 `whiteboard-cli --version`，确认版本为 `0.2.x`；未安装或版本不符 → `npm install -g @larksuite/whiteboard-cli@^0.2.0`
-> - 运行 `lark-cli --version`，确认可用。
-> - 执行任何 `npm install` 前，**必须征得用户同意**。
+> - 运行 `lark-cli --version`，确认可用，无需询问用户。
+> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 -v`，确认可用，无需询问用户。
 
 **CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**
 
@@ -126,15 +124,15 @@ diagram.png           ← 渲染结果
 
 ```bash
 # 第一步：dry-run 探测
-npx -y @larksuite/whiteboard-cli@^0.2.0 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <Token> \
     --source - --input_format raw \
     --idempotent-token <10+字符唯一串> \
     --overwrite --dry-run --as user
 
 # 第二步：确认后执行
-npx -y @larksuite/whiteboard-cli@^0.2.0 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <Token> \
     --source - --input_format raw \
diff --git a/skills/lark-whiteboard/references/lark-whiteboard-update.md b/skills/lark-whiteboard/references/lark-whiteboard-update.md
@@ -74,7 +74,7 @@ whiteboard-cli 工具的具体用法请参考 [§ 渲染 & 写入画板](../SKIL
 
 ```bash
 # 使用 whiteboard-cli 生成 OpenAPI 格式并通过管道传递
-npx -y @larksuite/whiteboard-cli@^0.2.0 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <画板Token> \
     --source - --input_format raw \
@@ -88,7 +88,7 @@ whiteboard-cli 工具的具体用法请参考 [§ 渲染 & 写入画板](../SKIL
 
 ```bash
 # 生成 OpenAPI 格式到文件
-npx -y @larksuite/whiteboard-cli@^0.2.0 -i <DSL 文件> --to openapi --format json -o ./temp.json
+npx -y @larksuite/whiteboard-cli@^0.2.9 -i <DSL 文件> --to openapi --format json -o ./temp.json
 
 # 从文件读取并更新
 lark-cli whiteboard +update \
diff --git a/skills/lark-whiteboard/references/layout.md b/skills/lark-whiteboard/references/layout.md
@@ -336,7 +336,7 @@ DSL 的语法是严格白名单，不能写原生 CSS 属性（不支持 `alignS
 先出骨架图导出坐标，再基于坐标补充连线和注解：
 
 ```bash
-npx -y @larksuite/whiteboard-cli@^0.2.0 -i skeleton.json -o step1.png -l coords.json
+npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords.json
 ```
 
 `coords.json` 包含每个带 id 节点的精确坐标（absX, absY, width, height）。
diff --git a/skills/lark-whiteboard/references/schema.md b/skills/lark-whiteboard/references/schema.md
@@ -323,14 +323,14 @@ lark-cli drive +upload --file ./beijing-palace.jpg
   x?: number; y?: number;
   width?: WBSizeValue;          // 默认 48
   height?: WBSizeValue;         // 默认 48，保持正方形
-  name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.0 --icons 输出中选取
+  name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.9 --icons 输出中选取
   color?: string;               // 可选颜色覆盖，hex 格式如 '#FF6600'
 }
 ```
 
 **获取可用图标**：规划好内容和布局后，运行以下命令查看所有可用图标名，从中选取：
 ```bash
-npx -y @larksuite/whiteboard-cli@^0.2.0 --icons
+npx -y @larksuite/whiteboard-cli@^0.2.9 --icons
 ```
 
 用法：
diff --git a/skills/lark-whiteboard/routes/dsl.md b/skills/lark-whiteboard/routes/dsl.md
@@ -13,7 +13,7 @@ Step 1: 路由 & 读取知识
 Step 2: 生成完整 DSL（含颜色）
   - 按 content.md 规划信息量和分组
   - 按 layout.md 选择布局模式和间距
-  - 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.0 --icons` 查看可用图标
+  - 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 --icons` 查看可用图标
   - 按 style.md 上色（用户没指定时用默认经典色板）
   - 按 schema.md 语法输出完整 JSON
   - 连线参考 connectors.md，排版参考 typography.md
@@ -25,12 +25,12 @@ Step 2: 生成完整 DSL（含颜色）
 
 Step 3: 渲染 & 审查 → 交付
   - 渲染前自查（见下方检查清单）
-  - 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.0 -i diagram.json -o diagram.png
+  - 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json -o diagram.png
   - 检查：信息完整？布局合理？配色协调？文字无截断？连线无交叉？
   - 有问题 → 按症状表修复 → 重新渲染（最多 2 轮）
   - 2 轮后仍有严重问题 → 考虑走 Mermaid 路径兜底
   - 写入画板：用 whiteboard-cli 将 diagram.json 转换为 OpenAPI 格式并 pipe 给 +update：
-      npx -y @larksuite/whiteboard-cli@^0.2.0 -i diagram.json --to openapi --format json \
+      npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json --to openapi --format json \
         | lark-cli whiteboard +update --whiteboard-token <board_token> \
             --source - --input_format raw --idempotent-token <时间戳+标识> --yes --as user
       → 完整 dry-run / 确认流程见 SKILL.md [§ 写入画板](../SKILL.md#写入画板)
diff --git a/skills/lark-whiteboard/routes/mermaid.md b/skills/lark-whiteboard/routes/mermaid.md
@@ -16,10 +16,10 @@ Step 3: 渲染验证 & 写入画板 & 交付
   1. 创建产物目录 ./diagrams/YYYY-MM-DDTHHMMSS/
   2. 保存为 diagram.mmd
   3. 渲染（仅用于预览验证，PNG 不是最终产物）：
-       npx -y @larksuite/whiteboard-cli@^0.2.0 -i diagram.mmd -o diagram.png
+       npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd -o diagram.png
   4. 审查 PNG，有问题修改后重新渲染（最多 2 轮）
   5. 写入画板：用 whiteboard-cli 将 diagram.mmd 转换为 OpenAPI 格式并 pipe 给 +update：
-       npx -y @larksuite/whiteboard-cli@^0.2.0 -i diagram.mmd --to openapi --format json \
+       npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd --to openapi --format json \
          | lark-cli whiteboard +update --whiteboard-token <board_token> \
              --source - --input_format raw --idempotent-token <时间戳+标识> --yes --as user
        → 完整 dry-run / 确认流程见 SKILL.md [§ 写入画板](../SKILL.md#写入画板)
diff --git a/skills/lark-whiteboard/routes/svg.md b/skills/lark-whiteboard/routes/svg.md
@@ -30,12 +30,12 @@
 ```
 建目录   ./diagrams/YYYY-MM-DDTHHMMSS/         (例：./diagrams/2026-04-15T143022/)
 写文件   <dir>/diagram.svg
-渲染     npx -y @larksuite/whiteboard-cli@^0.2.0 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg
-检查     npx -y @larksuite/whiteboard-cli@^0.2.0 -i <dir>/diagram.svg -f svg --check
-导出     npx -y @larksuite/whiteboard-cli@^0.2.0 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json
+渲染     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg
+检查     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --check
+导出     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json
 ```
 
-`npx -y @larksuite/whiteboard-cli@^0.2.0 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整
+`npx -y @larksuite/whiteboard-cli@^0.2.9 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整
 
 ## 画板怎么处理 SVG
 
diff --git a/skills/lark-whiteboard/scenes/bar-chart.md b/skills/lark-whiteboard/scenes/bar-chart.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.0` 渲染
+- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
 - **绝对定位手写**：简单柱状图（≤ 5 个柱）可手写坐标
 
 ## Layout 规则
diff --git a/skills/lark-whiteboard/scenes/fishbone.md b/skills/lark-whiteboard/scenes/fishbone.md
@@ -10,7 +10,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.0` 渲染
+- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/flywheel.md b/skills/lark-whiteboard/scenes/flywheel.md
@@ -9,7 +9,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.0` 渲染
+- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/line-chart.md b/skills/lark-whiteboard/scenes/line-chart.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.0` 渲染
+- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/treemap.md b/skills/lark-whiteboard/scenes/treemap.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.0` 渲染
+- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
 - 不适合手动心算坐标
 
 ## Layout 规则
PATCH

echo "Gold patch applied."
