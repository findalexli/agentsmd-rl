#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bria-skill

# Idempotency guard
if grep -qF "description: Generate, edit, and transform images with commercially-safe AI mode" "skills/bria-ai/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/bria-ai/SKILL.md b/skills/bria-ai/SKILL.md
@@ -1,10 +1,22 @@
 ---
 name: bria-ai
-description: Generate, edit, and transform images with commercially-safe AI models. Create images from text, edit by natural language instruction, remove backgrounds (transparent PNG), replace backgrounds, add/replace/remove objects, inpaint, outpaint, upscale (2x/4x), enhance quality, restyle (oil painting, anime, 3D), relight, reseason, restore old photos, colorize, sketch to photo, and product lifestyle shots. Use for websites, apps, presentations needing hero images, banners, product photos, product placement in scenes, icons, illustrations, or backgrounds. Also for e-commerce photography, batch generation, and pipelines. Triggers: image generation, generate/create image, edit photo, remove background, transparent PNG, replace background, product shot, lifestyle scenes, upscale, style transfer, photo restoration, colorize, sketch to image, outpaint, inpaint, cut out subject, integrate products into scene.
+description: Generate, edit, and transform images with commercially-safe AI models. Create images from text, edit by natural language instruction, remove backgrounds (transparent PNG), replace backgrounds, add/replace/remove objects, inpaint, outpaint, upscale (2x/4x), enhance quality, restyle (oil painting, anime, 3D), relight, reseason, restore old photos, colorize, sketch to photo, and product lifestyle shots. Use for websites, apps, presentations needing hero images, banners, product photos, product placement in scenes, icons, illustrations, or backgrounds. Also for e-commerce photography, batch generation, and pipelines. Triggers are image generation, generate/create image, edit photo, remove background, transparent PNG, replace background, product shot, lifestyle scenes, upscale, style transfer, photo restoration, colorize, sketch to image, outpaint, inpaint, cut out subject, integrate products into scene.
 license: MIT
 metadata:
   author: Bria AI
   version: "1.2.1"
+  dependencies:
+    - type: env
+      name: BRIA_API_KEY
+      description: "Bria AI API key (get one at https://platform.bria.ai/console/account/api-keys)"
+    - type: runtime
+      name: python
+      version: ">=3.8"
+      optional: true
+    - type: runtime
+      name: node
+      version: ">=18"
+      optional: true
 ---
 
 # Bria — Controllable Image Generation & Editing
PATCH

echo "Gold patch applied."
