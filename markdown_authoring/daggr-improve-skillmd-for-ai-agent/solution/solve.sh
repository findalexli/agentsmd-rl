#!/usr/bin/env bash
set -euo pipefail

cd /workspace/daggr

# Idempotency guard
if grep -qF "Find Spaces with semantic queries (describe what you need): `https://huggingface" ".agents/skills/daggr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/daggr/SKILL.md b/.agents/skills/daggr/SKILL.md
@@ -5,7 +5,7 @@ description: |
 license: MIT
 metadata:
   author: gradio-app
-  version: "1.0"
+  version: "1.1"
 ---
 
 # daggr
@@ -48,8 +48,8 @@ img = GradioNode("Tongyi-MAI/Z-Image-Turbo", api_name="/generate",
     outputs={"image": gr.Image()})
 ```
 
-Find Spaces with semantic queries (describe what you need): `https://huggingface.co/api/spaces/semantic-search?q=generate+music+for+a+video&sdk=gradio`
-Or by category: `https://huggingface.co/api/spaces/semantic-search?category=image-generation&sdk=gradio`
+Find Spaces with semantic queries (describe what you need): `https://huggingface.co/api/spaces/semantic-search?q=generate+music+for+a+video&sdk=gradio&includeNonRunning=false`
+Or by category: `https://huggingface.co/api/spaces/semantic-search?category=image-generation&sdk=gradio&includeNonRunning=false`
 (categories: image-generation | video-generation | text-generation | speech-synthesis | music-generation | voice-cloning | image-editing | background-removal | image-upscaling | ocr | style-transfer | image-captioning)
 
 ### FnNode - Python Functions
@@ -116,11 +116,10 @@ final = FnNode(fn=combine,
 ## Checklist
 
 1. **Check API** before using a Space:
-   ```python
-   from gradio_client import Client
-   Client("owner/space").view_api(return_format="dict")
+   ```bash
+   curl -s "https://<space-subdomain>.hf.space/gradio_api/openapi.json"
    ```
-   Or view OpenAPI spec: `https://<space-subdomain>.hf.space/gradio_api/openapi.json`
+   Replace `<space-subdomain>` with the Space's subdomain (e.g., `Tongyi-MAI/Z-Image-Turbo` → `tongyi-mai-z-image-turbo`).
    (Spaces also have "Use via API" link in footer with endpoints and code snippets)
 
 2. **Handle files** (Gradio returns dicts):
@@ -171,13 +170,7 @@ def combine(video: str|dict, audio: str|dict) -> str:
 ## Run
 
 ```bash
-uv pip install daggr  # Python 3.10+
-daggr workflow.py  # Starts server with hot reload at http://127.0.0.1:7860
-```
-
-**Troubleshooting:** Clear cache if you encounter stale state issues:
-```bash
-rm -rf ~/.cache/huggingface/daggr/*.db
+uvx --python 3.12 daggr workflow.py &  # Launch in background, hot reloads on file changes
 ```
 
 ## Authentication
PATCH

echo "Gold patch applied."
