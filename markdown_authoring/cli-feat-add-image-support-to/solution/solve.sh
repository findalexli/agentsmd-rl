#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "**\u8bc6\u522b\u5230\u56fe\u7247\u9700\u6c42\u540e**\uff1a\u53c2\u8003 [`references/image.md`](image.md) \u5b8c\u6210 Step 0\uff08\u56fe\u7247\u51c6\u5907\uff09\uff0c\u518d\u56de\u6765\u7ee7\u7eed\u5185\u5bb9\u89c4\u5212\u3002" "skills/lark-whiteboard/references/content.md" && grep -qF "**\u4e0d\u89e6\u53d1\u7684\u60c5\u51b5**\uff1a\u5373\u4f7f\u4e3b\u9898\u6d89\u53ca\u65c5\u884c\u3001\u7f8e\u98df\u3001\u4ea7\u54c1\u3001\u4eba\u7269\u7b49\u89c6\u89c9\u6027\u5185\u5bb9\uff0c\u53ea\u8981\u7528\u6237\u6ca1\u6709\u663e\u5f0f\u8bf4\u8981\u300c\u56fe\u7247/\u914d\u56fe/\u63d2\u56fe\u300d\uff0c\u5c31**\u4e00\u5f8b\u4e0d\u4f7f\u7528 image \u8282\u70b9**\uff0c\u7528\u6587\u5b57 " "skills/lark-whiteboard/references/image.md" && grep -qF "- image \u5bbd\u5ea6 = \u5361\u7247\u5bbd\u5ea6\uff0cheight \u6309 3:2 \u6bd4\u4f8b\uff08\u5982 240\u00d7160\uff09" "skills/lark-whiteboard/references/layout.md" && grep -qF "{ \"type\": \"text\", \"text\": \"\u4e16\u754c\u6700\u5927\u7684\u53e4\u4ee3\u5bab\u6bbf\u5efa\u7b51\u7fa4\", \"fontSize\": 11, \"textColor\": \"#666666\"" "skills/lark-whiteboard/references/schema.md" && grep -qF "| \u56fe\u7247\u5c55\u793a    | `scenes/photo-showcase.md` | \u7528\u6237\u663e\u5f0f\u8981\u6c42\u56fe\u7247/\u914d\u56fe/\u63d2\u56fe\u65f6         |" "skills/lark-whiteboard/routes/dsl.md" && grep -qF "{ \"type\": \"connector\", \"id\": \"c1\", \"connector\": { \"from\": \"stop-1\", \"to\": \"stop-" "skills/lark-whiteboard/scenes/photo-showcase.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-whiteboard/references/content.md b/skills/lark-whiteboard/references/content.md
@@ -4,6 +4,18 @@
 
 **用户 prompt 简短/模糊时**（如"画个漏斗图"、"画个架构图"），不要只输出字面内容。应适当补充该领域合理的内容
 
+## 图片需求识别
+
+> **在规划内容之前，先判断是否需要插入真实图片。**
+
+**触发条件（严格）**：仅当用户**显式说了**「图片、配图、插图、照片、真实图片、实拍」等词时，才使用 image 节点。
+
+**不触发**：即使主题是旅行、美食、产品等视觉性内容，只要用户没显式要求图片，就不使用 image 节点，用文字 + 形状 + icon 呈现。
+
+**识别到图片需求后**：参考 [`references/image.md`](image.md) 完成 Step 0（图片准备），再回来继续内容规划。
+
+**图片数量规划**：3-6 张为宜。少于 3 张显得单薄，多于 6 张增加准备时间且布局拥挤。
+
 ## 信息量参考
 
 | 用户需求 | 合理的信息量 |
diff --git a/skills/lark-whiteboard/references/image.md b/skills/lark-whiteboard/references/image.md
@@ -0,0 +1,57 @@
+# 图片资源处理
+
+## 图片需求识别
+
+**触发条件（严格）**：仅当用户**显式要求**使用图片时，才使用 image 节点。触发关键词：
+
+> 图片、配图、插图、照片、真实图片、实拍、放一张图、加个图、嵌入图片
+
+**不触发的情况**：即使主题涉及旅行、美食、产品、人物等视觉性内容，只要用户没有显式说要「图片/配图/插图」，就**一律不使用 image 节点**，用文字 + 形状 + icon 来呈现即可。
+
+识别到图片需求后，先完成下方 Step 0，再回到 [DSL 路径 Workflow](../routes/dsl.md) 继续 Step 2（生成 DSL）。
+
+**图片数量**：3-6 张为宜。
+
+## Step 0：图片准备
+
+1. 识别图片需求（见上方触发关键词表）
+2. 确定需要几张图，为每张图准备不同的搜索关键词（英文）
+3. 逐张下载 → 校验每张图不同（文件大小） → 逐张上传到飞书 Drive
+4. 收集所有 file_token，在 Step 2 生成 DSL 时引用
+
+## 上传步骤
+
+**单张图片**：
+```bash
+curl -L -o palace.jpg "https://example.com/palace.jpg"
+lark-cli drive +upload --file ./palace.jpg
+# 响应: { "file_token": "<file_token>", ... }
+```
+
+**多张图片（每张必须是不同的图）**：
+```bash
+# 1. 每张图用不同的搜索词/URL 下载
+curl -L -o forbidden-city.jpg "https://example.com/forbidden-city.jpg"
+curl -L -o great-wall.jpg "https://example.com/great-wall.jpg"
+curl -L -o temple.jpg "https://example.com/temple.jpg"
+
+# 2. 校验每张图确实不同（比较文件大小，跨平台通用）
+ls -l *.jpg   # 确认每张文件大小不同；若大小相同则内容可能重复，需重新下载
+
+# 3. 逐张上传，收集 token
+lark-cli drive +upload --file ./forbidden-city.jpg  # → <file_token_1>
+lark-cli drive +upload --file ./great-wall.jpg      # → <file_token_2>
+lark-cli drive +upload --file ./temple.jpg          # → <file_token_3>
+```
+
+> **多图常见错误**：用同一个 URL 参数下载多次，导致多张图片完全相同。每张图必须用不同的搜索关键词或不同的图片 ID。
+
+## 图片来源策略
+
+| 来源 | 方式 | 适用场景 |
+|------|------|----------|
+| 公开 URL | `curl -L -o file.jpg <URL>` 下载后上传 | 景点照片、开源图片 |
+| AI 生成 | 调用图片生成工具，保存后上传 | 插画、图标、概念图 |
+| 用户提供 | 用户给出本地路径或 URL | 产品截图、Logo |
+
+> `image.src` 必须是飞书 Drive 的 `file_token`，不支持直接使用 URL。所有图片都需要先上传。
diff --git a/skills/lark-whiteboard/references/layout.md b/skills/lark-whiteboard/references/layout.md
@@ -372,3 +372,14 @@ npx -y @larksuite/whiteboard-cli@^0.2.0 -i skeleton.json -o step1.png -l coords.
 ```
 
 `alignItems: 'stretch'` + `width: 'fill-container'` = 等宽等高。
+
+---
+
+## 图文卡片
+
+含图片的画板用图文卡片布局（vertical frame：图上文下）：
+
+- image 宽度 = 卡片宽度，height 按 3:2 比例（如 240×160）
+- 卡片间 gap: 24（比纯文字间距大）
+- 多卡片一行超过 3 张时，换行用嵌套 horizontal frame
+- 详见 `scenes/photo-showcase.md`
diff --git a/skills/lark-whiteboard/references/schema.md b/skills/lark-whiteboard/references/schema.md
@@ -237,6 +237,81 @@ SVG 通过 `image/svg+xml` Blob 加载到画布，**不在 HTML DOM 中**，因
   "svg": { "code": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#3B82F6\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"12\" r=\"10\"/><polyline points=\"12 6 12 12 16 14\"/></svg>" } }
 ```
 
+### Image（图片节点）
+
+在画板中嵌入图片。图片需先上传到飞书 Drive 获取 `file_token`。
+
+```typescript
+{
+  type: 'image';
+  id?: string;
+  x?: number; y?: number;
+  opacity?: number;              // 0-1
+  width: WBSizeValue;
+  height: WBSizeValue;
+  image: { src: string };        // 飞书 Drive file_token
+}
+```
+
+#### 使用要求
+
+图片必须先上传到飞书 Drive，`image.src` 填写返回的 `file_token`（如 `"T8SBbLB5co85YLxuX8icHAlrnZg"`）。
+
+**上传步骤**：
+```bash
+# 1. 上传图片到飞书 Drive
+lark-cli drive +upload --file ./beijing-palace.jpg
+
+# 2. 从响应中提取 file_token，填入 DSL
+```
+
+#### 尺寸建议
+
+| 用途 | 推荐尺寸 | 说明 |
+|------|----------|------|
+| 卡片插图 | 200×150 ~ 300×200 | 配合文字卡片使用 |
+| 全宽背景 | 与 frame 同宽，高度按比例 | 用于地图、背景板 |
+| 缩略图/头像 | 60×60 ~ 100×100 | 列表项中的小图 |
+
+> **宽高比**：建议保持原始图片的宽高比，避免拉伸变形。如果不确定原始比例，使用正方形（如 200×200）。
+
+#### 典型用法
+
+**1. 图文卡片**（图片 + 文字描述）
+
+```json
+{
+  "type": "frame", "layout": "vertical", "gap": 8, "padding": 0,
+  "width": 240, "height": "fit-content",
+  "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
+  "children": [
+    { "type": "image", "width": 240, "height": 160,
+      "image": { "src": "<file_token>" } },
+    { "type": "frame", "layout": "vertical", "gap": 4, "padding": [8, 12, 12, 12],
+      "width": "fill-container", "height": "fit-content",
+      "children": [
+        { "type": "text", "text": "故宫博物院", "fontSize": 14, "width": "fill-container", "height": "fit-content" },
+        { "type": "text", "text": "世界最大的古代宫殿建筑群", "fontSize": 11, "textColor": "#666666", "width": "fill-container", "height": "fit-content" }
+      ]
+    }
+  ]
+}
+```
+
+**2. 图片网格**（多张图片平铺）
+
+```json
+{
+  "type": "frame", "layout": "horizontal", "gap": 16, "padding": 16,
+  "width": "fit-content", "height": "fit-content",
+  "children": [
+    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_1>" } },
+    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_2>" } },
+    { "type": "image", "width": 200, "height": 150, "image": { "src": "<token_3>" } }
+  ]
+}
+```
+
 ### Icon（内置图标）
 
 引用画板内置图标库的图标。比手写 SVG 更简单——只需指定 `name`。
diff --git a/skills/lark-whiteboard/routes/dsl.md b/skills/lark-whiteboard/routes/dsl.md
@@ -73,6 +73,7 @@ Step 3: 渲染 & 审查 → 交付
 | 循环/飞轮图 | `scenes/flywheel.md`     | 增长飞轮、闭环链路                     |
 | 里程碑      | `scenes/milestone.md`    | 时间线、版本演进                       |
 | 流程图      | `scenes/flowchart.md`    | 业务流、状态机、带条件判断的链路       |
+| 图片展示    | `scenes/photo-showcase.md` | 用户显式要求图片/配图/插图时         |
 
 ## 渲染前自查
 
diff --git a/skills/lark-whiteboard/scenes/photo-showcase.md b/skills/lark-whiteboard/scenes/photo-showcase.md
@@ -0,0 +1,122 @@
+# 图片展示 (Photo Showcase)
+
+适用于：用户**显式要求使用图片/配图/插图**的场景（如"画一个带配图的旅行路线"、"做一个有图片的产品展示"）。
+
+> **注意**：仅当用户明确说了「图片/配图/插图/照片」等词时才进入本场景。单纯说"旅行路线图"、"产品展示"等不触发。
+> **前置条件**：进入本场景前，必须已完成 [`references/image.md`](../references/image.md) 的 Step 0（图片准备），拿到所有 file_token。
+
+## Content 约束
+
+- 图片 3-6 张，每张配标题（必需）+ 简短描述（可选，15字内）
+- **每张图必须是不同的真实图片**（不同 file_token），下载时用不同关键词/URL
+- 下载后用 `md5` 校验确保每张图不重复
+- 文字仅作辅助说明，图片是信息主体
+
+## Layout 选型
+
+| 模式 | 适用条件 | 特征 |
+|------|---------|------|
+| **卡片网格（默认）** | 多图平级展示（产品墙、团队介绍、美食推荐） | horizontal frame 内放等尺寸图文卡片 |
+| **路线时间线** | 有先后顺序（旅行路线、团建路线、项目演进） | 图文卡片 + connector 串联 |
+| **中心辐射** | 有一个核心主题 + 周围子项 | 中心标题 + 周围图文卡片 |
+
+## Layout 规则
+
+- **图文卡片结构**：vertical frame（图上文下），image 宽度 = 卡片宽度，height 按 3:2 比例
+- **卡片统一尺寸**：所有卡片宽高一致（推荐 240×280 或 200×250）
+- **图片统一尺寸**：所有 image 节点用相同 width/height（推荐 240×160 或 200×133）
+- **卡片间距**：gap: 24（比纯文字图表间距更大，让图片呼吸）
+- **卡片样式**：白色底 + 圆角 12 + 细边框，image 无圆角（紧贴卡片顶部）
+- **有序路线时**：卡片间用 connector 连接，connector 放顶层 nodes 数组
+
+## 骨架示例
+
+### 卡片网格（产品展示/团队介绍/美食推荐）
+
+```json
+{
+  "version": 2,
+  "nodes": [
+    {
+      "type": "frame", "id": "grid", "layout": "vertical", "gap": 24, "padding": 32,
+      "width": 840, "height": "fit-content",
+      "children": [
+        { "type": "text", "id": "title", "width": 776, "height": 36,
+          "text": "图表标题", "fontSize": 24, "textAlign": "center" },
+        {
+          "type": "frame", "id": "row", "layout": "horizontal", "gap": 24, "padding": 0,
+          "width": "fit-content", "height": "fit-content",
+          "children": [
+            {
+              "type": "frame", "id": "card-1", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
+              "width": 240, "height": "fit-content",
+              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
+              "children": [
+                { "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<token_1>" } },
+                { "type": "text", "id": "t-1", "text": "标题", "fontSize": 14, "width": 216, "height": 20 },
+                { "type": "text", "id": "d-1", "text": "简短描述", "fontSize": 11, "textColor": "#666666", "width": 216, "height": 16 }
+              ]
+            }
+          ]
+        }
+      ]
+    }
+  ]
+}
+```
+
+每张图文卡片结构相同，复制并替换 `<token_N>`、标题和描述即可。3 张卡片一行，超过 3 张换行（嵌套第二个 horizontal frame）。
+
+### 路线时间线（旅行路线/团建路线）
+
+```json
+{
+  "version": 2,
+  "nodes": [
+    {
+      "type": "frame", "id": "route", "layout": "vertical", "gap": 24, "padding": 32,
+      "width": 1100, "height": "fit-content",
+      "children": [
+        { "type": "text", "id": "title", "width": 1036, "height": 36,
+          "text": "路线标题", "fontSize": 24, "textAlign": "center" },
+        {
+          "type": "frame", "id": "stops", "layout": "horizontal", "gap": 32, "padding": 0,
+          "width": "fit-content", "height": "fit-content",
+          "children": [
+            {
+              "type": "frame", "id": "stop-1", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
+              "width": 240, "height": "fit-content",
+              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
+              "children": [
+                { "type": "image", "id": "img-1", "width": 240, "height": 160, "image": { "src": "<token_1>" } },
+                { "type": "text", "id": "t-1", "text": "第1站：地点名", "fontSize": 14, "width": 216, "height": 20 }
+              ]
+            },
+            {
+              "type": "frame", "id": "stop-2", "layout": "vertical", "gap": 8, "padding": [0, 0, 12, 0],
+              "width": 240, "height": "fit-content",
+              "fillColor": "#FFFFFF", "borderWidth": 1, "borderColor": "#E0E0E0", "borderRadius": 12,
+              "children": [
+                { "type": "image", "id": "img-2", "width": 240, "height": 160, "image": { "src": "<token_2>" } },
+                { "type": "text", "id": "t-2", "text": "第2站：地点名", "fontSize": 14, "width": 216, "height": 20 }
+              ]
+            }
+          ]
+        }
+      ]
+    },
+    { "type": "connector", "id": "c1", "connector": { "from": "stop-1", "to": "stop-2", "fromAnchor": "right", "toAnchor": "left" } }
+  ]
+}
+```
+
+注意：connector 必须放在**顶层 nodes 数组**，不能嵌套在 frame.children 内。connector 的属性须包裹在 `connector` 字段中。
+
+## 图片准备检查清单
+
+生成 DSL 前确认：
+
+- [ ] 所有 image 节点的 `image.src` 都是已上传的 file_token（非 URL）
+- [ ] 每个 file_token 不同（对应不同的真实图片）
+- [ ] 所有图片尺寸一致（同一画板内统一 width×height）
+- [ ] 图片宽高比合理（推荐 3:2，即 240×160）
PATCH

echo "Gold patch applied."
