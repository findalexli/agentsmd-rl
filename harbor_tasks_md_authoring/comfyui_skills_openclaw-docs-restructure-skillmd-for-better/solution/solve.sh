#!/usr/bin/env bash
set -euo pipefail

cd /workspace/comfyui-skills-openclaw

# Idempotency guard
if grep -qF "4. **Cloud Node Unauthorized**: Workflow uses cloud API nodes (Kling, Sora, etc." "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,7 +1,9 @@
 ---
 name: comfyui-skill-openclaw
 description: |
-  Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a single CLI. Import workflows, manage dependencies, execute across multiple servers, and track history — all through shell commands.
+  Run ComfyUI workflows from any AI agent (Claude Code, OpenClaw, Codex) via a single CLI.
+  Import workflows, manage dependencies, execute across multiple servers, and track history
+  — all through shell commands.
 
   **Use this Skill when:**
   (1) The user requests to "generate an image", "draw a picture", or "execute a ComfyUI workflow".
@@ -15,18 +17,28 @@ metadata:
 
 # ComfyUI Agent SKILL
 
-## Core Execution Specification
-
-As an Agent equipped with the ComfyUI skill, your objective is to translate the user's conversational requests into strict, structured parameters and execute workflows across multi-server environments.
-
-> **Prerequisites**: Install the CLI tool once: `pip install -U comfyui-skill-cli`. All commands must be run from this project's root directory.
+> **Prerequisites**: Install the CLI: `pip install -U comfyui-skill-cli`. All commands must run from this project's root directory (where this `SKILL.md` is located).
 >
 > [!IMPORTANT]
-> **Directory Sensitivity**: This CLI reads configuration from the local `config.json` and `data/` folder.
-> - **Mandatory**: You **MUST** `cd` into the comfyui-skill project root (where this `SKILL.md` is located) before running any command.
-> - **Symptom**: If `list` returns an empty array `[]` or `server status` reports a server as not found, you are likely in the wrong directory.
+> **Directory Sensitivity**: The CLI reads `config.json` and `data/` from the current directory.
+> You **MUST** `cd` into the project root before running any command.
+> **Symptom**: `list` returns `[]` or `server status` reports not found → you are in the wrong directory.
+
+## Quick Decision
+
+- User says "generate image / draw a picture" → **Execution Flow (Step 1–4)**
+- User says "import workflow / add workflow" → `comfyui-skill --json workflow import <path>`
+- User says "img2img / use this image" → first `comfyui-skill --json upload <image>`, then execute
+- User says "show previous results" → `comfyui-skill --json history list <id>`
+- User says "open management UI" → `python3 ./ui/open_ui.py`
+
+## Core Concepts
 
-### Quick Reference
+- **Skill ID**: `<server_id>/<workflow_id>` (e.g., `local/txt2img`). If server is omitted, the default server is used.
+- **Schema**: Each workflow has a `schema.json` that maps business parameter names (e.g., `prompt`, `seed`) to internal ComfyUI node fields. Never expose node IDs to the user.
+- **Server**: One or more ComfyUI instances configured in `config.json`. Check health with `server status`.
+
+## Command Reference
 
 | Command | Purpose |
 |---------|---------|
@@ -36,193 +48,120 @@ As an Agent equipped with the ComfyUI skill, your objective is to translate the
 | `comfyui-skill --json submit <id> --args '{...}'` | Submit a workflow (non-blocking) |
 | `comfyui-skill --json status <prompt_id>` | Check execution status |
 | `comfyui-skill --json run <id> --args '{...}'` | Execute a workflow (blocking) |
+| `comfyui-skill --json upload <image_path>` | Upload image to ComfyUI (for img2img workflows) |
 | `comfyui-skill --json deps check <id>` | Check missing dependencies |
 | `comfyui-skill --json deps install <id> --repos '[...]'` | Install missing custom nodes |
+| `comfyui-skill --json workflow import <path>` | Import workflow (auto-detect format, auto-generate schema) |
+| `comfyui-skill --json history list <id>` | List execution history for a workflow |
+| `comfyui-skill --json history show <id> <run_id>` | Show details of a specific run |
 
-Skill IDs use the format `<server_id>/<workflow_id>` (e.g., `local/txt2img`).
+---
 
-### UI Management Shortcut
+## Execution Flow
 
-If the user asks you to open, launch, or bring up the local Web UI for this skill, run:
+### Step 1: Query Available Workflows
 
 ```bash
-python3 ./ui/open_ui.py
+comfyui-skill --json list
 ```
 
-This command will:
-- reuse the UI if it is already running
-- start it in the background if it is not running
-- try to open the browser to the local dashboard automatically
+Returns a JSON array of all enabled workflows with their parameters.
 
-### Server Health Check
+- `required: true` parameters → **ask the user** if not provided.
+- `required: false` parameters → infer from context (e.g., `seed` = random number), or omit.
+- Never expose node IDs; only use business parameter names (e.g., prompt, style).
+- If multiple workflows match, pick the most relevant one or list candidates.
 
-Before running a workflow, check whether the target ComfyUI server is online:
+### Step 2: Parameter Assembly
 
-```bash
-comfyui-skill --json server status
+Assemble parameters into a JSON string. Example:
+```
+{"prompt": "A beautiful landscape, high quality, masterpiece", "seed": 40128491}
 ```
 
-This returns JSON with `"status": "online"` or `"status": "offline"`.
-
-**Recommended agent flow:** Before Step 3 (Trigger Image Generation), run a server status check. If offline, ask the user to start ComfyUI and retry once it is online.
-
-### Step 0: Workflow Onboarding and Import (Optional)
-
-Use the manager UI/API when the user wants to register workflows into this skill instead of running them immediately.
-
-- For bulk import from ComfyUI `/userdata`, local files, manager API routes, and import result semantics, read [`references/workflow-import.md`](./references/workflow-import.md).
-- Prefer the bulk import flow when the user wants to sync many saved workflows at once.
-- Use single-workflow configuration only when the user gives one workflow and wants a targeted setup.
-
-#### Single-workflow auto-configuration
+If critical parameters are missing, ask the user (e.g., "What visual style would you like?").
 
-If the user provides you with one new ComfyUI workflow JSON (API format) and asks you to "configure it" or "add it":
-1. Check the existing server configurations or default to `local`.
-2. Save the provided JSON file to `./data/<server_id>/<new_workflow_id>/workflow.json`.
-3. Analyze the JSON structure (look for `inputs` inside node definitions, e.g., `KSampler`'s `seed`, `CLIPTextEncode`'s `text` for positive/negative prompts, `EmptyLatentImage` for width/height).
-4. Automatically generate a schema mapping file and save it to `./data/<server_id>/<new_workflow_id>/schema.json`. The schema format must follow:
-   ```json
-   {
-     "workflow_id": "<new_workflow_id>",
-     "server_id": "<server_id>",
-     "description": "Auto-configured by Agent",
-     "enabled": true,
-     "parameters": {
-       "prompt": { "node_id": "3", "field": "text", "required": true, "type": "string", "description": "Positive prompt" }
-     }
-   }
-   ```
-5. Tell the user that the new workflow on the specific server is successfully configured and ready to be used.
+### Step 3: Pre-flight Dependency Check
 
-### Step 1: Query Available Workflows (Registry)
+**Always** run before first execution of a workflow:
 
-Before attempting to generate any image, you must **first query the registry** to understand which workflows are currently supported and enabled:
 ```bash
-comfyui-skill --json list
+comfyui-skill --json deps check <server_id>/<workflow_id>
 ```
 
-**Return Format Parsing**:
-You will receive a JSON array containing all available workflows. Each is uniquely identified by the combination of `server_id` and `workflow_id` (or path format `<server_id>/<workflow_id>`):
-- For parameters with `required: true`, if the user hasn't provided them, you must **ask the user to provide them**.
-- For parameters with `required: false`, you can infer and generate them yourself based on the user's description (e.g., translating and optimizing the user's scene), or simply use empty values/random numbers (e.g., `seed` = random number).
-- Never expose underlying node information to the user (do not mention Node IDs); only ask about business parameter names (e.g., prompt, style).
-- If multiple workflows match the user prompt across different servers, you may list them acting as candidates, OR simply pick the most relevant one and execute it directly to provide the best user experience.
-
-### Step 2: Parameter Assembly and Interaction
+- If `is_ready` is `true` → proceed to Step 4.
+- If `is_ready` is `false`:
+  1. Present missing nodes and models to the user.
+  2. If user agrees to install, run:
+     ```bash
+     comfyui-skill --json deps install <id> --repos '["https://github.com/repo1"]'
+     ```
+     Use `source_repo` URLs from the check report as `--repos` values.
+  3. If `needs_restart` is `true`, inform the user to restart ComfyUI, then re-check.
+  4. Missing models must be downloaded manually — tell the user which folder to place them in (e.g., `checkpoints`).
 
-Once you have identified the workflow to use and collected/generated all necessary parameters, you need to assemble them into a compact JSON string.
-For example, if the schema exposes `prompt` and `seed`, you need to construct:
-`{"prompt": "A beautiful landscape, high quality, masterpiece", "seed": 40128491}`
+### Step 4: Execute the Workflow
 
-*If critical parameters are missing, politely ask the user. For example: "To generate the image you need, would you like a specific person or animal? Do you have an expected visual style?"*
+> **Note**: JSON args must be wrapped in single quotes to prevent bash from parsing double quotes.
 
-### Step 2.5: Pre-flight Dependency Check (Automatic)
+Choose the execution mode based on your environment:
 
-Before executing a workflow, **always** run a dependency check to verify that all required custom nodes and models are available on the ComfyUI server:
+#### Interactive mode: `submit` + `status` (recommended for chat)
 
+**Step 4a — Submit:**
 ```bash
-comfyui-skill --json deps check <server_id>/<workflow_id>
+comfyui-skill --json submit <id> --args '{"prompt": "..."}'
 ```
+Returns: `{"status": "submitted", "prompt_id": "..."}`. Tell the user generation has started.
 
-**Return format:**
-```json
-{
-  "is_ready": false,
-  "missing_nodes": [
-    {"class_type": "SAMDetectorCombined", "can_auto_install": false}
-  ],
-  "missing_models": [
-    {"filename": "model.safetensors", "folder": "checkpoints", "loader_node": "CheckpointLoaderSimple", "node_id": "4"}
-  ],
-  "total_nodes_required": 12,
-  "total_nodes_installed": 11
-}
+**Step 4b — Poll:**
+```bash
+comfyui-skill --json status <prompt_id>
 ```
 
-**Agent behavior:**
-1. If `is_ready` is `true` → proceed to Step 3 directly.
-2. If `is_ready` is `false` → present the dependency report to the user in a clear, formatted message:
-   - List missing custom nodes with package names and whether they can be auto-installed.
-   - List missing models with filenames and which folder they belong to.
-   - Ask the user: "Do you want me to install the missing custom nodes?"
-3. If the user agrees to install, run:
-   ```bash
-   comfyui-skill --json deps install <server_id>/<workflow_id> --repos '["https://github.com/repo1", "https://github.com/repo2"]'
-   ```
-   Use the `source_repo` URLs from the dependency check report as `--repos` values. This returns installation results for each package. Report the results to the user.
-   - If `needs_restart` is `true`, inform the user that ComfyUI needs to restart for changes to take effect.
-   - After restart, re-run `check-deps` to confirm everything is resolved, then proceed to Step 3.
-4. For missing models: inform the user that models must be downloaded manually, and tell them which folder to place the files in (e.g., "Please download `model.safetensors` and place it in the `checkpoints` folder").
-
-### Step 3: Trigger the Image Generation Task
-
-Once the complete parameters are collected and the dependency check passes, execute the workflow.
+Status values: `queued` (with `position`) → `running` → `success` (with `outputs`) or `error`.
 
-> **Note**: Outer curly braces must be wrapped in single quotes to prevent bash from incorrectly parsing JSON double quotes.
+**Polling pattern — critical for real-time feedback:**
 
-There are two execution modes. Choose based on your environment:
+Each `status` call must be a **separate tool invocation** (a separate bash command). Do NOT write a shell loop. The correct pattern is:
 
-- **Interactive** (chat, messaging, or any context where the user is waiting): use `submit` + `status` so you can send progress updates between polls.
-- **Non-interactive** (scripted pipelines, CI, or terminal-only): use the blocking one-shot mode for simplicity.
-
-#### Interactive mode: `submit` + `status`
-
-**Step 3a — Submit the job:**
-```bash
-comfyui-skill --json submit <server_id>/<workflow_id> --args '{"key1": "value1", "key2": 123}'
-```
-Returns immediately:
-```json
-{"status": "submitted", "prompt_id": "91f87917-3b0b-4d0f-8768-356f8d18c2e6"}
-```
+1. Run `status` as a standalone bash command.
+2. Read the returned JSON.
+3. If `queued` or `running`: **send a text message to the user** with progress, then run `status` again.
+4. If `success`: proceed to Step 5.
+5. If `error`: report the error.
 
-After receiving the response, tell the user that image generation has started.
+#### Non-interactive mode: one-shot blocking (for scripts/CI)
 
-**Step 3b — Poll for progress:**
 ```bash
-comfyui-skill --json status <prompt_id>
+comfyui-skill --json run <id> --args '{"prompt": "..."}'
 ```
-Returns immediately with the current state:
-- `{"status": "queued", "prompt_id": "...", "position": 2}` — waiting in line
-- `{"status": "running", "prompt_id": "..."}` — ComfyUI is actively generating
-- `{"status": "success", "prompt_id": "...", "outputs": [{"filename": "ComfyUI_00001_.png", "subfolder": "", "type": "output"}]}` — done
-- `{"status": "not_found", "prompt_id": "..."}` — job not found in queue or history
-- `{"status": "error", "prompt_id": "...", "error": "..."}` — generation failed
+Blocks until finished. Returns the same result format as `status` with `success`.
 
-**Polling pattern — this is critical for real-time feedback:**
+### Step 5: Present Results
 
-Each `status` call must be a **separate tool invocation** (i.e., a separate bash command). Do NOT write a shell loop or combine multiple status checks into one command. The correct pattern is:
+On success, the result contains an `outputs` array with file references (`filename`, `subfolder`, `type`).
+Use your native capabilities to present the files to the user (e.g., image preview, file path).
 
-1. Run `status` as a standalone bash command.
-2. Read the returned JSON.
-3. If `"queued"` or `"running"`: **send a text message to the user** with the current progress (e.g., "Queued at position 2…", "Generating…"), then run `status` again as another standalone bash command.
-4. If `"success"`: proceed to Step 4.
-5. If `"error"`: report the error.
+---
 
-This ensures each progress update is delivered to the user immediately, rather than being batched at the end.
+## Workflow Import
 
-#### Non-interactive mode: one-shot blocking
+When the user wants to add new workflows (not execute existing ones):
 
 ```bash
-comfyui-skill --json run <server_id>/<workflow_id> --args '{"key1": "value1", "key2": 123}'
+comfyui-skill --json workflow import <json_path> --check-deps
 ```
-Blocks until ComfyUI finishes, then returns the full result:
-```json
-{"status": "success", "prompt_id": "...", "outputs": [{"filename": "ComfyUI_00001_.png", "subfolder": "", "type": "output"}]}
-```
-
-**Result format (both modes)**:
-- On success: JSON with `prompt_id` and an `outputs` array containing ComfyUI output file references (filename, subfolder, type).
-- On error: JSON with `error` code and message.
 
-The manager stores execution history per workflow, including raw args, resolved args, prompt ID, result files, status, timing, and error summary. History records live under `data/<server_id>/<workflow_id>/history/`.
+- Supports both API format and editor format (auto-detected, auto-converted).
+- Automatically generates `schema.json` with smart parameter extraction.
+- Use `--check-deps` to verify dependencies immediately after import.
 
-### Step 4: Send the Image to the User
+For bulk import from ComfyUI server or local folders, see [`references/workflow-import.md`](./references/workflow-import.md).
 
-Once you obtain the output filenames from the result, use your native capabilities to present the files to the user (e.g., in an OpenClaw environment, returning the path allows the client to intercept it and convert it into rich text or an image preview).
+## Troubleshooting
 
-## Common Troubleshooting & Notices
-1. **ComfyUI Offline**: If the CLI returns a connection error, run `comfyui-skill --json server status` and ask the user to start the ComfyUI service before retrying.
-2. **Schema Not Found**: If you directly called a workflow the user mentioned verbally, but the CLI reports it not found, run `comfyui-skill --json list` and tell the user they need to first go to the Web UI panel to upload and configure the mapping for that workflow on the desired server.
-3. **Parameter Format Error**: Ensure that the JSON passed via `--args` is a valid JSON string wrapped in single quotes.
-4. **Cloud Node Unauthorized**: If a workflow fails with "Unauthorized: Please login first to use this node", the workflow uses ComfyUI cloud API nodes (e.g., Kling, Sora, Nano Banana). The user needs to configure a ComfyUI API Key in the server settings. Guide them to: (1) Go to https://platform.comfy.org to generate an API Key, (2) Open the Web UI panel → Server Settings → fill in the "ComfyUI API Key" field.
+1. **ComfyUI Offline**: Run `comfyui-skill --json server status`. If offline, ask the user to start ComfyUI.
+2. **Workflow Not Found**: Run `comfyui-skill --json list` to see available workflows. If missing, the user needs to import it first.
+3. **Parameter Format Error**: Ensure `--args` is valid JSON wrapped in single quotes.
+4. **Cloud Node Unauthorized**: Workflow uses cloud API nodes (Kling, Sora, etc.). Guide user to: (1) Generate an API Key at https://platform.comfy.org, (2) Open Web UI → Server Settings → fill in "ComfyUI API Key".
PATCH

echo "Gold patch applied."
