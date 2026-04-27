#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bria-skill

# Idempotency guard
if grep -qF "**Rule of thumb**: If the task requires *creating new visual content* or *unders" "skills/image-utils/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/image-utils/SKILL.md b/skills/image-utils/SKILL.md
@@ -20,6 +20,24 @@ Pillow-based utilities for deterministic pixel-level image operations. Use for r
 - **Web optimization**: Compress and resize for fast delivery
 - **Social media preparation**: Crop to platform-specific aspect ratios
 
+## When NOT to Use This Skill — Use `bria-ai` Instead
+
+This skill handles **deterministic pixel-level operations** only. For any **generative or AI-powered** image work, use the `bria-ai` skill instead:
+
+- **Generating images from text prompts** → use `bria-ai`
+- **AI background removal or replacement** → use `bria-ai`
+- **AI image editing (inpainting, object removal/addition)** → use `bria-ai`
+- **Style transfer or AI-driven visual effects** → use `bria-ai`
+- **Creating product lifestyle shots with AI** → use `bria-ai`
+- **Image upscaling with AI super-resolution** → use `bria-ai`
+
+**Rule of thumb**: If the task requires *creating new visual content* or *understanding image semantics*, use `bria-ai`. If the task requires *transforming existing pixels* (resize, crop, format convert, watermark), use this skill.
+
+If `bria-ai` is not available, install it with:
+```bash
+npx skills add bria-ai/bria-skill
+```
+
 ## Quick Reference
 
 | Operation | Method | Description |
PATCH

echo "Gold patch applied."
