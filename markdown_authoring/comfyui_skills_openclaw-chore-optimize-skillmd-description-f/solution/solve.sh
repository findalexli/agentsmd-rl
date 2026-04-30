#!/usr/bin/env bash
set -euo pipefail

cd /workspace/comfyui-skills-openclaw

# Idempotency guard
if grep -qF "Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a sin" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: comfyui-skill-openclaw
 description: |
-  Generate images utilizing ComfyUI's powerful node-based workflow capabilities. Supports dynamically loading multiple pre-configured generation workflows from different instances and their corresponding parameter mappings, importing saved workflows in bulk from ComfyUI or local JSON files, converting natural language into parameters, driving local or remote ComfyUI services, tracking execution history with parameters and results, and ultimately returning the images to the target client.
+  Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a single CLI. Import workflows, manage dependencies, execute across multiple servers, and track history — all through shell commands.
 
   **Use this Skill when:**
   (1) The user requests to "generate an image", "draw a picture", or "execute a ComfyUI workflow".
PATCH

echo "Gold patch applied."
