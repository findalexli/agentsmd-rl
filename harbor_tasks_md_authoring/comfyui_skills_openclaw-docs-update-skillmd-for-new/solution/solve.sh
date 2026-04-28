#!/usr/bin/env bash
set -euo pipefail

cd /workspace/comfyui-skills-openclaw

# Idempotency guard
if grep -qF "| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect, " "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -29,7 +29,12 @@ metadata:
 - User says "generate image / draw a picture" → **Execution Flow (Step 1–4)**
 - User says "import workflow / add workflow" → `comfyui-skill --json workflow import <path>`
 - User says "img2img / use this image" → first `comfyui-skill --json upload <image>`, then execute
+- User says "inpainting / mask this area" → `comfyui-skill --json upload <mask> --mask`, then execute
 - User says "show previous results" → `comfyui-skill --json history list <id>`
+- User says "what failed / check job status" → `comfyui-skill --json jobs list --status failed`
+- User says "which server has more VRAM" → `comfyui-skill --json server stats --all`
+- User says "what nodes are available" → `comfyui-skill --json nodes list`
+- User says "dry run / test without executing" → `comfyui-skill --json run <id> --validate`
 - User says "open management UI" → `python3 ./ui/open_ui.py`
 
 ## Core Concepts
@@ -43,17 +48,21 @@ metadata:
 | Command | Purpose |
 |---------|---------|
 | `comfyui-skill --json server status` | Check if ComfyUI server is online |
+| `comfyui-skill --json server stats` | Show VRAM, RAM, GPU, versions (`--all` for multi-server) |
 | `comfyui-skill --json list` | List all available workflows and parameters |
 | `comfyui-skill --json info <id>` | Show workflow details and parameter schema |
 | `comfyui-skill --json submit <id> --args '{...}'` | Submit a workflow (non-blocking) |
 | `comfyui-skill --json status <prompt_id>` | Check execution status |
-| `comfyui-skill --json run <id> --args '{...}'` | Execute a workflow (blocking) |
-| `comfyui-skill --json upload <image_path>` | Upload image to ComfyUI (for img2img workflows) |
+| `comfyui-skill --json run <id> --args '{...}'` | Execute a workflow (blocking, real-time streaming) |
+| `comfyui-skill --json run <id> --validate` | Validate workflow without executing |
+| `comfyui-skill --json upload <path>` | Upload image to ComfyUI (for img2img workflows) |
+| `comfyui-skill --json upload <path> --mask` | Upload mask image (for inpainting workflows) |
+| `comfyui-skill --json nodes list` | List all available ComfyUI nodes |
+| `comfyui-skill --json jobs list` | List server-side job history (`--status failed` to filter) |
 | `comfyui-skill --json deps check <id>` | Check missing dependencies |
 | `comfyui-skill --json deps install <id> --repos '[...]'` | Install missing custom nodes |
-| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect format, auto-generate schema) |
+| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect, warns about deprecated nodes) |
 | `comfyui-skill --json history list <id>` | List execution history for a workflow |
-| `comfyui-skill --json history show <id> <run_id>` | Show details of a specific run |
 
 ---
 
@@ -150,12 +159,12 @@ Use your native capabilities to present the files to the user (e.g., image previ
 When the user wants to add new workflows (not execute existing ones):
 
 ```bash
-comfyui-skill --json workflow import <json_path> --check-deps
+comfyui-skill --json workflow import <json_path>
 ```
 
 - Supports both API format and editor format (auto-detected, auto-converted).
 - Automatically generates `schema.json` with smart parameter extraction.
-- Use `--check-deps` to verify dependencies immediately after import.
+- After import, check dependencies before first execution.
 
 For bulk import from ComfyUI server or local folders, see [`references/workflow-import.md`](./references/workflow-import.md).
 
PATCH

echo "Gold patch applied."
