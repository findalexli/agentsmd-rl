#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bria-skill

# Idempotency guard
if grep -qF "Use alongside the **[bria-ai skill](https://clawhub.ai/galbria/bria-ai)** to pos" "skills/image-utils/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/image-utils/SKILL.md b/skills/image-utils/SKILL.md
@@ -260,19 +260,21 @@ with open("optimized.webp", "wb") as f:
     f.write(optimized_bytes)
 ```
 
-## Integration with AI Image Generation
+## Integration with Bria AI
 
-Use with Bria AI or other image generation APIs:
+Use alongside the **[bria-ai skill](https://clawhub.ai/galbria/bria-ai)** to post-process AI-generated images. Generate or edit images with Bria's API, then use image-utils for resizing, cropping, watermarking, and web optimization.
 
 ```python
-from bria_client import BriaClient
+import requests
 from image_utils import ImageUtils
 
-client = BriaClient()
-
-# Generate with AI
-result = client.generate("product photo of headphones", aspect_ratio="1:1")
-image_url = result['result']['image_url']
+# Generate with Bria AI (see bria-ai skill for full API reference)
+response = requests.post(
+    "https://engine.prod.bria-api.com/v2/image/generate",
+    headers={"api_token": BRIA_API_KEY, "Content-Type": "application/json"},
+    json={"prompt": "product photo of headphones", "aspect_ratio": "1:1", "sync": True}
+)
+image_url = response.json()["result"]["image_url"]
 
 # Download and post-process
 image = ImageUtils.load_from_url(image_url)
PATCH

echo "Gold patch applied."
