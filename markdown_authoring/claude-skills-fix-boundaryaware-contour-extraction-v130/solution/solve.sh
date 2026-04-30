#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "- `edge_density > 0.15`: Keeps shapes with even modest edge alignment. Previous " "image-to-svg/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/image-to-svg/SKILL.md b/image-to-svg/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: image-to-svg
-version: 1.1.0
+version: 1.2.0
 description: Convert raster images (photos, paintings, illustrations) into SVG vector reproductions. Use when the user uploads an image and asks to reproduce, vectorize, trace, or convert it to SVG. Also use when asked to decompose an image into shapes, create an SVG version of a picture, or faithfully reproduce artwork as vector graphics. Do NOT use for creating original SVG illustrations from text descriptions — only for converting existing raster images.
 ---
  
@@ -146,7 +146,7 @@ for cid, cnt in sorted_clusters:
             edge_density = edge_overlap.sum() / max(contour_mask.sum(), 1)
             
             # Keep if: compact (real dark area), edge-aligned, or large
-            if not (compactness > 0.15 or edge_density > 0.3
+            if not (compactness > 0.08 or edge_density > 0.15
                     or area > (h_orig * w_orig * 0.01)):
                 continue  # Skip: thin dark boundary artifact
         
@@ -170,8 +170,8 @@ for cid, cnt in sorted_clusters:
 **Tuning**:
 - `DARK_LUM_THRESHOLD`: 55 works broadly; lower for dark images, higher for bright
 - Dilation kernel: 3×3 is the sweet spot. **Do NOT use 5×5** — causes blotchy artifacts in hair/foliage.
-- `compactness > 0.15`: Keeps circles/squares, filters ribbons
-- `edge_density > 0.3`: Keeps shapes aligned with real structural edges
+- `compactness > 0.08`: Keeps all but the thinnest ribbon artifacts. Previous value of 0.15 was too aggressive — filtered real facial detail.
+- `edge_density > 0.15`: Keeps shapes with even modest edge alignment. Previous value of 0.3 filtered legitimate dark features like nostrils, lip shadows, brow lines.
  
 ## Step 5: Z-Ordering (Painter's Algorithm)
  
PATCH

echo "Gold patch applied."
