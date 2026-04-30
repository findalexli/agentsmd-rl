#!/usr/bin/env bash
set -euo pipefail

cd /workspace/image-router

# Idempotency guard
if grep -qF "- **Do not paste API keys into chat**. Set the env var in the OpenClaw Gateway e" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,14 +1,23 @@
 ---
-name: imagerouter
+name: image-router
 description: Generate Images with any AI model on ImageRouter (requires API key).
 homepage: https://imagerouter.io
-metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["curl"]}}}
+metadata: {"openclaw":{"emoji":"🎨","requires":{"bins":["curl"]},"primaryEnv":"IMAGEROUTER_API_KEY"}}
 ---
 
 # [ImageRouter](https://imagerouter.io) AI Image Generation
 
 Generate images with any AI model available on [ImageRouter](https://imagerouter.io).
 
+## OpenClaw Setup
+
+- This skill expects your ImageRouter key in the environment variable `IMAGEROUTER_API_KEY`.
+- **Do not paste API keys into chat**. Set the env var in the OpenClaw Gateway environment (in terminal) and restart the gateway. Example:
+```bash
+openclaw config set skills.entries.image-router.apiKey "your_api_key_here"
+openclaw gateway restart
+```
+
 ## Available models
 The `test/test` model is a free dummy model that is used for testing the API. It is not a real model, therefore you should use other models for image generation.
 
@@ -32,7 +41,7 @@ curl "https://api.imagerouter.io/v1/models?type=image&sort=date&limit=1000"
 Basic generation with JSON endpoint:
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/generations' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   --json '{
     "prompt": "a serene mountain landscape at sunset",
     "model": "test/test",
@@ -48,7 +57,7 @@ curl 'https://api.imagerouter.io/v1/openai/images/generations' \
 ### Text-to-Image with multipart/form-data:
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/edits' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   -F 'prompt=a cyberpunk city at night' \
   -F 'model=test/test' \
   -F 'quality=high' \
@@ -60,7 +69,7 @@ curl 'https://api.imagerouter.io/v1/openai/images/edits' \
 ### Image-to-Image (with input images):
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/edits' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   -F 'prompt=transform this into a watercolor painting' \
   -F 'model=test/test' \
   -F 'quality=auto' \
@@ -73,7 +82,7 @@ curl 'https://api.imagerouter.io/v1/openai/images/edits' \
 ### Multiple images (up to 16):
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/edits' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   -F 'prompt=combine these images' \
   -F 'model=test/test' \
   -F 'image[]=@image1.webp' \
@@ -84,7 +93,7 @@ curl 'https://api.imagerouter.io/v1/openai/images/edits' \
 ### With mask (some models require mask for inpainting):
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/edits' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   -F 'prompt=fill the masked area with flowers' \
   -F 'model=test/test' \
   -F 'image[]=@original.webp' \
@@ -141,14 +150,14 @@ curl 'https://api.imagerouter.io/v1/openai/images/edits' \
 ### Quick test generation:
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/generations' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   --json '{"prompt":"test image","model":"test/test"}'
 ```
 
 ### Download image directly:
 ```bash
 curl 'https://api.imagerouter.io/v1/openai/images/generations' \
-  -H 'Authorization: Bearer YOUR_API_KEY' \
+  -H "Authorization: Bearer $IMAGEROUTER_API_KEY" \
   --json '{"prompt":"abstract art","model":"test/test"}' \
   | jq -r '.data[0].url' \
   | xargs curl -o output.webp
PATCH

echo "Gold patch applied."
