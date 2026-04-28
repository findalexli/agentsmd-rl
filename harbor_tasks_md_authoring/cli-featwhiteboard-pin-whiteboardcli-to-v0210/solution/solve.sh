#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.10 -i <\u4ea7\u7269\u6587\u4ef6> --to openapi --format json \\" "skills/lark-whiteboard/SKILL.md" && grep -qF "skills/lark-whiteboard/references/content.md" "skills/lark-whiteboard/references/content.md" && grep -qF "lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --paren" "skills/lark-whiteboard/references/image.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.10 -i <DSL \u6587\u4ef6> --to openapi --format json " "skills/lark-whiteboard/references/lark-whiteboard-update.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.10 -i skeleton.json -o step1.png -l coords" "skills/lark-whiteboard/references/layout.md" && grep -qF "> - `image.src` \u5fc5\u987b\u662f\u901a\u8fc7 `docs +media-upload --parent-type whiteboard --parent-node" "skills/lark-whiteboard/references/schema.md" && grep -qF "- \u6e32\u67d3 PNG\uff08\u4ec5\u7528\u4e8e\u9884\u89c8\u9a8c\u8bc1\uff0c\u4e0d\u662f\u6700\u7ec8\u4ea7\u7269\uff09\uff1anpx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.jso" "skills/lark-whiteboard/routes/dsl.md" && grep -qF "npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd --to openapi --format js" "skills/lark-whiteboard/routes/mermaid.md" && grep -qF "\u5bfc\u51fa     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -f svg --to" "skills/lark-whiteboard/routes/svg.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1a\u7528 .cjs \u811a\u672c\u8ba1\u7b97\u67f1\u4f53\u4f4d\u7f6e\u548c\u9ad8\u5ea6\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteboar" "skills/lark-whiteboard/scenes/bar-chart.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u5fc5\u987b\uff09\uff1a\u7528 .cjs \u811a\u672c\u901a\u8fc7\u4e09\u89d2\u51fd\u6570\u8ba1\u7b97\u9c7c\u9aa8\u5750\u6807\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteb" "skills/lark-whiteboard/scenes/fishbone.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u5fc5\u987b\uff09\uff1a\u7528 .cjs \u811a\u672c\u6781\u5750\u6807\u8ba1\u7b97\u9636\u6bb5\u6807\u7b7e\u4f4d\u7f6e\u3001SVG \u5706\u73af\u5207\u5272\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuit" "skills/lark-whiteboard/scenes/flywheel.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1a\u7528 .cjs \u811a\u672c\u8ba1\u7b97\u6570\u636e\u70b9\u5750\u6807\u548c\u6298\u7ebf\u8def\u5f84\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @larksuite/whiteb" "skills/lark-whiteboard/scenes/line-chart.md" && grep -qF "- [ ] \u6240\u6709 image \u8282\u70b9\u7684 `image.src` \u90fd\u662f\u901a\u8fc7 `docs +media-upload --parent-type whiteboard" "skills/lark-whiteboard/scenes/photo-showcase.md" && grep -qF "- **\u811a\u672c\u751f\u6210\u5750\u6807**\uff08\u63a8\u8350\uff09\uff1aTreemap \u9700\u8981\u7cbe\u786e\u7684\u9762\u79ef\u6bd4\u4f8b\u8ba1\u7b97\uff0c\u7528 .cjs \u811a\u672c\u9012\u5f52\u5207\u5206\u77e9\u5f62\uff0c\u811a\u672c\u8f93\u51fa JSON \u6587\u4ef6\u540e\u8c03\u7528 `npx -y @la" "skills/lark-whiteboard/scenes/treemap.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-whiteboard/SKILL.md b/skills/lark-whiteboard/SKILL.md
@@ -13,7 +13,7 @@ metadata:
 
 > [!IMPORTANT]
 > - 运行 `lark-cli --version`，确认可用，无需询问用户。
-> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 -v`，确认可用，无需询问用户。
+> - 运行 `npx -y @larksuite/whiteboard-cli@^0.2.10 -v`，确认可用，无需询问用户。
 
 **CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**
 
@@ -124,15 +124,15 @@ diagram.png           ← 渲染结果
 
 ```bash
 # 第一步：dry-run 探测
-npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <Token> \
     --source - --input_format raw \
     --idempotent-token <10+字符唯一串> \
     --overwrite --dry-run --as user
 
 # 第二步：确认后执行
-npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <Token> \
     --source - --input_format raw \
diff --git a/skills/lark-whiteboard/references/content.md b/skills/lark-whiteboard/references/content.md
@@ -4,18 +4,6 @@
 
 **用户 prompt 简短/模糊时**（如"画个漏斗图"、"画个架构图"），不要只输出字面内容。应适当补充该领域合理的内容
 
-## 图片需求识别
-
-> **在规划内容之前，先判断是否需要插入真实图片。**
-
-**触发条件（严格）**：仅当用户**显式说了**「图片、配图、插图、照片、真实图片、实拍」等词时，才使用 image 节点。
-
-**不触发**：即使主题是旅行、美食、产品等视觉性内容，只要用户没显式要求图片，就不使用 image 节点，用文字 + 形状 + icon 呈现。
-
-**识别到图片需求后**：参考 [`references/image.md`](image.md) 完成 Step 0（图片准备），再回来继续内容规划。
-
-**图片数量规划**：3-6 张为宜。少于 3 张显得单薄，多于 6 张增加准备时间且布局拥挤。
-
 ## 信息量参考
 
 | 用户需求 | 合理的信息量 |
diff --git a/skills/lark-whiteboard/references/image.md b/skills/lark-whiteboard/references/image.md
@@ -1,57 +1,80 @@
-# 图片资源处理
+# 图片准备 (Image Preparation)
 
-## 图片需求识别
+> 本文件说明如何在画板 DSL 中使用图片节点。进入任何含图片的场景前，必须先完成图片准备流程。
 
-**触发条件（严格）**：仅当用户**显式要求**使用图片时，才使用 image 节点。触发关键词：
+## 概述
 
-> 图片、配图、插图、照片、真实图片、实拍、放一张图、加个图、嵌入图片
+画板 DSL 支持 `type: 'image'` 节点，但图片不能直接使用 URL，必须先上传到飞书获取 **media token**，然后在 DSL 中引用。
 
-**不触发的情况**：即使主题涉及旅行、美食、产品、人物等视觉性内容，只要用户没有显式说要「图片/配图/插图」，就**一律不使用 image 节点**，用文字 + 形状 + icon 来呈现即可。
+**关键约束**：
+- 图片 token 必须通过 `docs +media-upload --parent-type whiteboard` 上传获取
+- 图片必须上传到**目标画板**（`--parent-node` 设为目标画板 token），跨画板的 token 不可用
+- `drive +upload` 获取的 Drive file token **不能**用于画板图片节点
 
-识别到图片需求后，先完成下方 Step 0，再回到 [DSL 路径 Workflow](../routes/dsl.md) 继续 Step 2（生成 DSL）。
+## Step 0：图片准备流程
 
-**图片数量**：3-6 张为宜。
+### 1. 下载图片
 
-## Step 0：图片准备
+用 `curl` 下载图片到本地。**必须使用能根据关键词返回相关图片的图片源**。
 
-1. 识别图片需求（见上方触发关键词表）
-2. 确定需要几张图，为每张图准备不同的搜索关键词（英文）
-3. 逐张下载 → 校验每张图不同（文件大小） → 逐张上传到飞书 Drive
-4. 收集所有 file_token，在 Step 2 生成 DSL 时引用
+**推荐图片源**：
 
-## 上传步骤
+| 图片源类型 | 说明 |
+|-------|------|
+| 免费版权图库 | 支持按关键词搜索，图片无版权风险（CC0 或类似协议），图库种类丰富（人物/动物/风景/美食/建筑等），关键词能精准匹配图片内容 |
+| 直接 URL | 用户提供或已知的图片链接，最可靠 |
+
+**选择图库的必要条件**：
+- **版权合规**：图片必须无版权纠纷风险，避免使用需要付费授权或有使用限制的图库
+- **关键词搜索**：支持按关键词搜索并返回相关图片，确保图片内容与主题匹配
+- **内容丰富**：图库图片种类多、数量大，能覆盖常见主题（宠物、美食、景点、产品等）
 
-**单张图片**：
 ```bash
-curl -L -o palace.jpg "https://example.com/palace.jpg"
-lark-cli drive +upload --file ./palace.jpg
-# 响应: { "file_token": "<file_token>", ... }
+curl -L -o photo1.jpg "<图片URL>"
+curl -L -o photo2.jpg "<图片URL>"
 ```
 
-**多张图片（每张必须是不同的图）**：
-```bash
-# 1. 每张图用不同的搜索词/URL 下载
-curl -L -o forbidden-city.jpg "https://example.com/forbidden-city.jpg"
-curl -L -o great-wall.jpg "https://example.com/great-wall.jpg"
-curl -L -o temple.jpg "https://example.com/temple.jpg"
+**严禁使用随机占位图服务**：某些图库仅提供随机占位图，URL 中的关键词参数不会影响返回的图片内容，下载的图片与主题完全无关。
 
-# 2. 校验每张图确实不同（比较文件大小，跨平台通用）
+### 2. 校验图片
+
+```bash
 ls -l *.jpg   # 确认每张文件大小不同；若大小相同则内容可能重复，需重新下载
+```
+
+**图片内容审查（必须执行）**：
+- 下载完成后，确认文件是真实图片而非 HTML 错误页：若某张图片大小 < 1KB，很可能是下载失败返回了 HTML 错误页，需重新下载
+- **图片内容正确性只能在渲染后验证**：生成 DSL 并本地渲染 PNG 后，必须查看渲染结果，确认每张图片内容与主题相关（如宠物主题的图片确实是宠物，而非建筑/风景等不相关内容）
+- 若发现图片内容与主题不符，必须用更精确的关键词重新下载并重新上传
+
+### 3. 上传到目标画板
 
-# 3. 逐张上传，收集 token
-lark-cli drive +upload --file ./forbidden-city.jpg  # → <file_token_1>
-lark-cli drive +upload --file ./great-wall.jpg      # → <file_token_2>
-lark-cli drive +upload --file ./temple.jpg          # → <file_token_3>
+**必须**使用 `docs +media-upload --parent-type whiteboard` 上传：
+
+```bash
+lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>
+# 响应: { "file_token": "<media_token>", ... }
 ```
 
-> **多图常见错误**：用同一个 URL 参数下载多次，导致多张图片完全相同。每张图必须用不同的搜索关键词或不同的图片 ID。
+逐张上传，收集每个 media token：
 
-## 图片来源策略
+```bash
+lark-cli docs +media-upload --file ./photo1.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_1>
+lark-cli docs +media-upload --file ./photo2.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_2>
+lark-cli docs +media-upload --file ./photo3.jpg --parent-type whiteboard --parent-node <whiteboard_token>  # → <media_token_3>
+```
+
+### 4. 在 DSL 中引用
+
+```json
+{ "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<media_token_1>" } }
+```
 
-| 来源 | 方式 | 适用场景 |
-|------|------|----------|
-| 公开 URL | `curl -L -o file.jpg <URL>` 下载后上传 | 景点照片、开源图片 |
-| AI 生成 | 调用图片生成工具，保存后上传 | 插画、图标、概念图 |
-| 用户提供 | 用户给出本地路径或 URL | 产品截图、Logo |
+## 常见错误
 
-> `image.src` 必须是飞书 Drive 的 `file_token`，不支持直接使用 URL。所有图片都需要先上传。
+| 错误现象 | 原因 | 解决 |
+|---------|------|------|
+| 画板 API 返回 500（2891001） | 使用了 Drive file token 而非 media token | 改用 `docs +media-upload --parent-type whiteboard` |
+| 画板 API 返回 500 | 图片上传到了其他画板 | 重新上传到目标画板 |
+| 图片裂开/无法显示 | token 无效或已过期 | 重新上传获取新 token |
+| 图片内容与主题无关 | 使用了随机占位图服务 | 改用免费版权图库服务 |
diff --git a/skills/lark-whiteboard/references/lark-whiteboard-update.md b/skills/lark-whiteboard/references/lark-whiteboard-update.md
@@ -74,7 +74,7 @@ whiteboard-cli 工具的具体用法请参考 [§ 渲染 & 写入画板](../SKIL
 
 ```bash
 # 使用 whiteboard-cli 生成 OpenAPI 格式并通过管道传递
-npx -y @larksuite/whiteboard-cli@^0.2.9 -i <产物文件> --to openapi --format json \
+npx -y @larksuite/whiteboard-cli@^0.2.10 -i <产物文件> --to openapi --format json \
   | lark-cli whiteboard +update \
     --whiteboard-token <画板Token> \
     --source - --input_format raw \
@@ -88,7 +88,7 @@ whiteboard-cli 工具的具体用法请参考 [§ 渲染 & 写入画板](../SKIL
 
 ```bash
 # 生成 OpenAPI 格式到文件
-npx -y @larksuite/whiteboard-cli@^0.2.9 -i <DSL 文件> --to openapi --format json -o ./temp.json
+npx -y @larksuite/whiteboard-cli@^0.2.10 -i <DSL 文件> --to openapi --format json -o ./temp.json
 
 # 从文件读取并更新
 lark-cli whiteboard +update \
diff --git a/skills/lark-whiteboard/references/layout.md b/skills/lark-whiteboard/references/layout.md
@@ -336,7 +336,7 @@ DSL 的语法是严格白名单，不能写原生 CSS 属性（不支持 `alignS
 先出骨架图导出坐标，再基于坐标补充连线和注解：
 
 ```bash
-npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords.json
+npx -y @larksuite/whiteboard-cli@^0.2.10 -i skeleton.json -o step1.png -l coords.json
 ```
 
 `coords.json` 包含每个带 id 节点的精确坐标（absX, absY, width, height）。
@@ -372,14 +372,3 @@ npx -y @larksuite/whiteboard-cli@^0.2.9 -i skeleton.json -o step1.png -l coords.
 ```
 
 `alignItems: 'stretch'` + `width: 'fill-container'` = 等宽等高。
-
----
-
-## 图文卡片
-
-含图片的画板用图文卡片布局（vertical frame：图上文下）：
-
-- image 宽度 = 卡片宽度，height 按 3:2 比例（如 240×160）
-- 卡片间 gap: 24（比纯文字间距大）
-- 多卡片一行超过 3 张时，换行用嵌套 horizontal frame
-- 详见 `scenes/photo-showcase.md`
diff --git a/skills/lark-whiteboard/references/schema.md b/skills/lark-whiteboard/references/schema.md
@@ -116,6 +116,30 @@ interface WBDocument {
 > 需要手算固定尺寸时：`实际文字宽/高 + 对应 inset`。
 > 例：rect 内 14px 字号两行文字高 ~32px → `height >= 32 + 24 = 56px`
 
+### Image（图片节点）
+
+图片节点用于在画板中展示图片。图片不能直接使用 URL，必须先上传到飞书获取 media token。
+
+```typescript
+{
+  type: 'image';
+  id?: string;
+  x?: number; y?: number;
+  width: WBSizeValue;           // 固定宽度，推荐 240 或 200
+  height: WBSizeValue;          // 固定高度，推荐按 3:2 比例（如 240×160 或 200×133）
+  image: {
+    src: string;                // media token（通过 docs +media-upload --parent-type whiteboard 上传获取）
+  };
+}
+```
+
+> **关键约束**：
+> - `image.src` 必须是通过 `docs +media-upload --parent-type whiteboard --parent-node <画板token>` 上传后返回的 **media token**，不能是 URL 或 Drive file token
+> - 图片必须上传到**目标画板**，跨画板的 token 不可用
+> - 同一画板内所有 image 节点应使用统一的 width/height，保持视觉一致
+> - 图片宽高比推荐 3:2（如 240×160），避免变形
+> - 详细上传流程见 [`references/image.md`](image.md)
+
 ### Text（纯文本节点）
 
 ```typescript
@@ -237,81 +261,6 @@ SVG 通过 `image/svg+xml` Blob 加载到画布，**不在 HTML DOM 中**，因
   "svg": { "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#3B82F6\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><polyline points=\"12 6 12 12 16 14\"/></svg>" } }
 ```
 
-### Image（图片节点）
-
-在画板中嵌入图片。图片需先上传到飞书 Drive 获取 `file_token`。
-
-```typescript
-{
-  type: 'image';
-  id?: string;
-  x?: number; y?: number;
-  opacity?: number;              // 0-1
-  width: WBSizeValue;
-  height: WBSizeValue;
-  image: { src: string };        // 飞书 Drive file_token
-}
-```
-
-#### 使用要求
-
-图片必须先上传到飞书 Drive，`image.src` 填写返回的 `file_token`（如 `"T8SBbLB5co85YLxuX8icHAlrnZg"`）。
-
-**上传步骤**：
-```bash
-# 1. 上传图片到飞书 Drive
-lark-cli drive +upload --file ./beijing-palace.jpg
-
-# 2. 从响应中提取 file_token，填入 DSL
-```
-
-#### 尺寸建议
-
-| 用途 | 推荐尺寸 | 说明 |
-|------|----------|------|
-| 卡片插图 | 200×150 ~ 300×200 | 配合文字卡片使用 |
-| 全宽背景 | 与 frame 同宽，高度按比例 | 用于地图、背景板 |
-| 缩略图/头像 | 60×60 ~ 100×100 | 列表项中的小图 |
-
-> **宽高比**：建议保持原始图片的宽高比，避免拉伸变形。如果不确定原始比例，使用正方形（如 200×200）。
-
-#### 典型用法
-
-**1. 图文卡片**（图片 + 文字描述）
-
-```json
-{
-  "type": "frame", "layout": "vertical", "gap": 8, "padding": 0,
-  "width": 240, "height": "fit-content",
-  "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
-  "children": [
-    { "type": "image", "width": 240, "height": 160,
-      "image": { "src": "<file_token>" } },
-    { "type": "frame", "layout": "vertical", "gap": 4, "padding": [8, 12, 12, 12],
-      "width": "fill-container", "height": "fit-content",
-      "children": [
-        { "type": "text", "text": "故宫博物院", "fontSize": 14, "width": "fill-container", "height": "fit-content" },
-        { "type": "text", "text": "世界最大的古代宫殿建筑群", "fontSize": 11, "textColor": "#666666", "width": "fill-container", "height": "fit-content" }
-      ]
-    }
-  ]
-}
-```
-
-**2. 图片网格**（多张图片平铺）
-
-```json
-{
-  "type": "frame", "layout": "horizontal", "gap": 16, "padding": 16,
-  "width": "fit-content", "height": "fit-content",
-  "children": [
-    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_1>" } },
-    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_2>" } },
-    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_3>" } }
-  ]
-}
-```
-
 ### Icon（内置图标）
 
 引用画板内置图标库的图标。比手写 SVG 更简单——只需指定 `name`。
@@ -323,14 +272,14 @@ lark-cli drive +upload --file ./beijing-palace.jpg
   x?: number; y?: number;
   width?: WBSizeValue;          // 默认 48
   height?: WBSizeValue;         // 默认 48，保持正方形
-  name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.9 --icons 输出中选取
+  name: string;                 // 图标名称，从 npx -y @larksuite/whiteboard-cli@^0.2.10 --icons 输出中选取
   color?: string;               // 可选颜色覆盖，hex 格式如 '#FF6600'
 }
 ```
 
 **获取可用图标**：规划好内容和布局后，运行以下命令查看所有可用图标名，从中选取：
 ```bash
-npx -y @larksuite/whiteboard-cli@^0.2.9 --icons
+npx -y @larksuite/whiteboard-cli@^0.2.10 --icons
 ```
 
 用法：
diff --git a/skills/lark-whiteboard/routes/dsl.md b/skills/lark-whiteboard/routes/dsl.md
@@ -13,7 +13,7 @@ Step 1: 路由 & 读取知识
 Step 2: 生成完整 DSL（含颜色）
   - 按 content.md 规划信息量和分组
   - 按 layout.md 选择布局模式和间距
-  - 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.9 --icons` 查看可用图标
+  - 推荐使用图标让图表更直观，运行 `npx -y @larksuite/whiteboard-cli@^0.2.10 --icons` 查看可用图标
   - 按 style.md 上色（用户没指定时用默认经典色板）
   - 按 schema.md 语法输出完整 JSON
   - 连线参考 connectors.md，排版参考 typography.md
@@ -25,12 +25,12 @@ Step 2: 生成完整 DSL（含颜色）
 
 Step 3: 渲染 & 审查 → 交付
   - 渲染前自查（见下方检查清单）
-  - 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json -o diagram.png
+  - 渲染 PNG（仅用于预览验证，不是最终产物）：npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json -o diagram.png
   - 检查：信息完整？布局合理？配色协调？文字无截断？连线无交叉？
   - 有问题 → 按症状表修复 → 重新渲染（最多 2 轮）
   - 2 轮后仍有严重问题 → 考虑走 Mermaid 路径兜底
   - 写入画板：用 whiteboard-cli 将 diagram.json 转换为 OpenAPI 格式并 pipe 给 +update：
-      npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.json --to openapi --format json \
+      npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.json --to openapi --format json \
         | lark-cli whiteboard +update --whiteboard-token <board_token> \
             --source - --input_format raw --idempotent-token <时间戳+标识> --yes --as user
       → 完整 dry-run / 确认流程见 SKILL.md [§ 写入画板](../SKILL.md#写入画板)
@@ -73,7 +73,7 @@ Step 3: 渲染 & 审查 → 交付
 | 循环/飞轮图 | `scenes/flywheel.md`     | 增长飞轮、闭环链路                     |
 | 里程碑      | `scenes/milestone.md`    | 时间线、版本演进                       |
 | 流程图      | `scenes/flowchart.md`    | 业务流、状态机、带条件判断的链路       |
-| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时         |
+| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时（需先完成 `references/image.md` 的图片准备） |
 
 ## 渲染前自查
 
diff --git a/skills/lark-whiteboard/routes/mermaid.md b/skills/lark-whiteboard/routes/mermaid.md
@@ -16,10 +16,10 @@ Step 3: 渲染验证 & 写入画板 & 交付
   1. 创建产物目录 ./diagrams/YYYY-MM-DDTHHMMSS/
   2. 保存为 diagram.mmd
   3. 渲染（仅用于预览验证，PNG 不是最终产物）：
-       npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd -o diagram.png
+       npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd -o diagram.png
   4. 审查 PNG，有问题修改后重新渲染（最多 2 轮）
   5. 写入画板：用 whiteboard-cli 将 diagram.mmd 转换为 OpenAPI 格式并 pipe 给 +update：
-       npx -y @larksuite/whiteboard-cli@^0.2.9 -i diagram.mmd --to openapi --format json \
+       npx -y @larksuite/whiteboard-cli@^0.2.10 -i diagram.mmd --to openapi --format json \
          | lark-cli whiteboard +update --whiteboard-token <board_token> \
              --source - --input_format raw --idempotent-token <时间戳+标识> --yes --as user
        → 完整 dry-run / 确认流程见 SKILL.md [§ 写入画板](../SKILL.md#写入画板)
diff --git a/skills/lark-whiteboard/routes/svg.md b/skills/lark-whiteboard/routes/svg.md
@@ -30,12 +30,12 @@
 ```
 建目录   ./diagrams/YYYY-MM-DDTHHMMSS/         (例：./diagrams/2026-04-15T143022/)
 写文件   <dir>/diagram.svg
-渲染     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg
-检查     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --check
-导出     npx -y @larksuite/whiteboard-cli@^0.2.9 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json
+渲染     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -o <dir>/diagram.png -f svg
+检查     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -f svg --check
+导出     npx -y @larksuite/whiteboard-cli@^0.2.10 -i <dir>/diagram.svg -f svg --to openapi --format json > <dir>/diagram.json
 ```
 
-`npx -y @larksuite/whiteboard-cli@^0.2.9 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整
+`npx -y @larksuite/whiteboard-cli@^0.2.10 --check` 检测 `text-overflow` 和 `node-overlap`, 并结合视觉效果(查看 PNG)进行调整
 
 ## 画板怎么处理 SVG
 
diff --git a/skills/lark-whiteboard/scenes/bar-chart.md b/skills/lark-whiteboard/scenes/bar-chart.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
+- **脚本生成坐标**（推荐）：用 .cjs 脚本计算柱体位置和高度，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染
 - **绝对定位手写**：简单柱状图（≤ 5 个柱）可手写坐标
 
 ## Layout 规则
diff --git a/skills/lark-whiteboard/scenes/fishbone.md b/skills/lark-whiteboard/scenes/fishbone.md
@@ -10,7 +10,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
+- **脚本生成坐标**（必须）：用 .cjs 脚本通过三角函数计算鱼骨坐标，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/flywheel.md b/skills/lark-whiteboard/scenes/flywheel.md
@@ -9,7 +9,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
+- **脚本生成坐标**（必须）：用 .cjs 脚本极坐标计算阶段标签位置、SVG 圆环切割，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/line-chart.md b/skills/lark-whiteboard/scenes/line-chart.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
+- **脚本生成坐标**（推荐）：用 .cjs 脚本计算数据点坐标和折线路径，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染
 
 ## Layout 规则
 
diff --git a/skills/lark-whiteboard/scenes/photo-showcase.md b/skills/lark-whiteboard/scenes/photo-showcase.md
@@ -3,13 +3,14 @@
 适用于：用户**显式要求使用图片/配图/插图**的场景（如"画一个带配图的旅行路线"、"做一个有图片的产品展示"）。
 
 > **注意**：仅当用户明确说了「图片/配图/插图/照片」等词时才进入本场景。单纯说"旅行路线图"、"产品展示"等不触发。
-> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 file_token。
+
+> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 media token。
 
 ## Content 约束
 
 - 图片 3-6 张，每张配标题（必需）+ 简短描述（可选，15字内）
-- **每张图必须是不同的真实图片**（不同 file_token），下载时用不同关键词/URL
-- 下载后用 `md5` 校验确保每张图不重复
+- **每张图必须是不同的真实图片**（不同 media token），下载时用不同关键词/URL
+- 下载后用 `ls -l` 比较文件大小确保每张图不重复
 - 文字仅作辅助说明，图片是信息主体
 
 ## Layout 选型
@@ -116,7 +117,10 @@
 
 生成 DSL 前确认：
 
-- [ ] 所有 image 节点的 `image.src` 都是已上传的 file_token（非 URL）
-- [ ] 每个 file_token 不同（对应不同的真实图片）
+- [ ] 所有 image 节点的 `image.src` 都是通过 `docs +media-upload --parent-type whiteboard` 上传的 media token（非 URL、非 Drive file token）
+- [ ] 所有图片已上传到目标画板（`--parent-node` 设为目标画板 token）
+- [ ] 每个 media token 不同（对应不同的真实图片）
 - [ ] 所有图片尺寸一致（同一画板内统一 width×height）
 - [ ] 图片宽高比合理（推荐 3:2，即 240×160）
+- [ ] 渲染 PNG 后查看图片内容，确认每张图片与主题相关
+- [ ] 未使用随机占位图服务（关键词参数不影响返回内容的图库）
diff --git a/skills/lark-whiteboard/scenes/treemap.md b/skills/lark-whiteboard/scenes/treemap.md
@@ -8,7 +8,7 @@
 
 ## Layout 选型
 
-- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.9` 渲染
+- **脚本生成坐标**（推荐）：Treemap 需要精确的面积比例计算，用 .cjs 脚本递归切分矩形，脚本输出 JSON 文件后调用 `npx -y @larksuite/whiteboard-cli@^0.2.10` 渲染
 - 不适合手动心算坐标
 
 ## Layout 规则
PATCH

echo "Gold patch applied."
