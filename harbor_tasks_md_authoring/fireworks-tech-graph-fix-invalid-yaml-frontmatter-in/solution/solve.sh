#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fireworks-tech-graph

# Idempotency guard
if grep -qF "Use when the user wants to create any technical diagram - architecture, data" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,7 +1,11 @@
 ---
 name: fireworks-tech-graph
 
-description: "Use when the user wants to create any technical diagram, including architecture, data flow, flowchart, sequence, agent or memory, or concept map, and export it as SVG plus PNG. Trigger on requests like 画图, 帮我画, 生成图, 做个图, 架构图, 流程图, 可视化一下, 出图, generate diagram, draw diagram, or visualize."
+  Use when the user wants to create any technical diagram - architecture, data
+  flow, flowchart, sequence, agent/memory, or concept map - and export as
+  SVG+PNG. Trigger on: "画图" "帮我画" "生成图" "做个图" "架构图" "流程图"
+  "可视化一下" "出图" "generate diagram" "draw diagram" "visualize" or any
+  system/flow description the user wants illustrated.
 
 
 # Fireworks Tech Graph
PATCH

echo "Gold patch applied."
