#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-007-agents

# Idempotency guard
if grep -qF ".claude/agents/ai/computer-vision-specialist.md" ".claude/agents/ai/computer-vision-specialist.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/ai/computer-vision-specialist.md b/.claude/agents/ai/computer-vision-specialist.md
@@ -1,6 +1,8 @@
 ---
 name: computer-vision-specialist
 description: Computer Vision and image processing specialist focused on developing advanced computer vision systems, implementing deep learning models for visual r
+---
+
 # Computer Vision Specialist Agent
 
 ## Role
PATCH

echo "Gold patch applied."
