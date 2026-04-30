#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aworld

# Idempotency guard
if grep -qF "examples/skill_agent/skills/code/skill.md" "examples/skill_agent/skills/code/skill.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/examples/skill_agent/skills/code/skill.md b/examples/skill_agent/skills/code/skill.md
@@ -1,3 +1,4 @@
+---
 name: hypercode_forge
 description: 🚀 HyperCode Forge - Competitive compression engine for MCP workflows
 tool_list: {"terminal-server": ["execute_command"], "filesystem-server": ["write_file", "read_file"], "ms-playwright": []}
PATCH

echo "Gold patch applied."
