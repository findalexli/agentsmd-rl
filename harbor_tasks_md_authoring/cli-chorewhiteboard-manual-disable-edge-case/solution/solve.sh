#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "\u601d\u7ef4\u5bfc\u56fe\uff0c\u65f6\u5e8f\u56fe\uff0c\u7c7b\u56fe\uff0c\u997c\u56fe\uff0c\u6d41\u7a0b\u56fe\u7b49\u56fe\u8868\u63a8\u8350\u4f7f\u7528 Mermaid/PlantUML \u8bed\u6cd5\u7ed8\u5236\u3002" "skills/lark-whiteboard/references/lark-whiteboard-update.md" && grep -qF "\u753b\u677f\u7684 svg-parser \u628a\u53ef\u8bc6\u522b\u5143\u7d20\u8f6c\u6210\u53ef\u7f16\u8f91\u8282\u70b9, \u5176\u4f59\u964d\u7ea7\u4e3a\u5185\u5d4c\u56fe\u7247(\u6e32\u67d3\u6ca1\u95ee\u9898, \u867d\u7136\u4e0d\u53ef\u7f16\u8f91, \u4f46\u662f\u53ef\u4ee5\u6b63\u5e38\u663e\u793a)\uff1b\u4f46 `<radialGradi" "skills/lark-whiteboard/routes/svg.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/lark-whiteboard/references/lark-whiteboard-update.md b/skills/lark-whiteboard/references/lark-whiteboard-update.md
@@ -24,7 +24,7 @@
 
 **不要以直接生成 json 语法的方式创作 raw 格式的飞书 OpenAPI 原生画板节点参数**
 
-思维导图，时序图，类图，饼图，流程图等图标推荐使用 Mermaid/PlantUML 语法绘制。
+思维导图，时序图，类图，饼图，流程图等图表推荐使用 Mermaid/PlantUML 语法绘制。
 
 而当需要绘制架构图，组织架构图，泳道图，对比图，鱼骨图，柱状图，折线图，树状图，漏斗图，金字塔图，循环/飞轮图，里程碑或其他较为复杂的图表时，推荐参考 [§ 渲染 & 写入画板](../SKILL.md#渲染--写入画板) 使用 whiteboard-cli 工具创作。
 
diff --git a/skills/lark-whiteboard/routes/svg.md b/skills/lark-whiteboard/routes/svg.md
@@ -39,7 +39,8 @@
 
 ## 画板怎么处理 SVG
 
-画板的 svg-parser 把可识别元素转成可编辑节点, 其余降级为内嵌图片(渲染没问题, 虽然不可编辑, 但是可以正常显示), **不需要所有元素都可编辑, 一定要兼顾可编辑和美观漂亮**
+画板的 svg-parser 把可识别元素转成可编辑节点, 其余降级为内嵌图片(渲染没问题, 虽然不可编辑, 但是可以正常显示)；但 `<radialGradient>` / `<filter>` / `<clipPath>` 等装饰特性画板完全不支持，会导致渲染问题（见下方⚠️）
+**不需要所有元素都可编辑, 但必须避免使用不支持的装饰特性, 且要兼顾可编辑和美观漂亮**
 
 **可识别的元素**
 
@@ -49,5 +50,5 @@
 - 分组：`<g>` / `<a>` / `<use>` 引用 `<symbol>`
 - 变换：`translate` / `rotate` / `scale` 正常；`skewX` / `skewY` / `matrix(...)` 降级
 
-**装饰特性**
-- `<radialGradient>` / `<filter>` / `<pattern>` / `<clipPath>` / `<mask>` → 画板通过图片路径保留视觉 (光晕/阴影/纹理/遮罩等效果都在, 元素不可再编辑但不丢视觉)
+**⚠️ [!IMPORTANT] 不支持的装饰特性**
+- `<radialGradient>` / `<filter>` / `<pattern>` / `<clipPath>` / `<mask>` → 画板都不支持，**请避免使用，否则会导致画板渲染问题**
PATCH

echo "Gold patch applied."
