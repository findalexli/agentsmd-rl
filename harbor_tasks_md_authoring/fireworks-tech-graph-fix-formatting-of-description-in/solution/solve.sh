#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fireworks-tech-graph

# Idempotency guard
if grep -qF "description: 'Use when the user wants to create any technical diagram \u2014 architec" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: fireworks-tech-graph
-description: Use when the user wants to create any technical diagram — architecture, data flow, flowchart, sequence, agent/memory, or concept map — and export as SVG+PNG. Trigger on: "画图" "帮我画" "生成图" "做个图" "架构图" "流程图" "可视化一下" "出图" "generate diagram" "draw diagram" "visualize" or any system/flow description the user wants illustrated.
+description: 'Use when the user wants to create any technical diagram — architecture, data flow, flowchart, sequence, agent/memory, or concept map — and export as SVG+PNG. Trigger on: "画图" "帮我画" "生成图" "做个图" "架构图" "流程图" "可视化一下" "出图" "generate diagram" "draw diagram" "visualize" or any system/flow description the user wants illustrated.'
 ---
 
 # Fireworks Tech Graph
PATCH

echo "Gold patch applied."
