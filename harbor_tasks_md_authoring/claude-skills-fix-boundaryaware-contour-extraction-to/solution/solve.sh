#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "**Why this works**: Boundary artifacts are thin (low compactness) AND don't corr" "image-to-svg/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/image-to-svg/SKILL.md b/image-to-svg/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: image-to-svg
-version: 1.0.0
+version: 1.1.0
 description: Convert raster images (photos, paintings, illustrations) into SVG vector reproductions. Use when the user uploads an image and asks to reproduce, vectorize, trace, or convert it to SVG. Also use when asked to decompose an image into shapes, create an SVG version of a picture, or faithfully reproduce artwork as vector graphics. Do NOT use for creating original SVG illustrations from text descriptions — only for converting existing raster images.
 ---
  
@@ -15,7 +15,7 @@ Convert raster images into faithful SVG reproductions using data-driven color qu
 ## Pipeline Overview
  
 ```
-Source Image → Preprocessing → Color Quantization → Contour Extraction → SVG Assembly
+Source Image → Preprocessing → Color Quantization → Edge Map → Contour Extraction → SVG Assembly
 ```
  
 ## Step 1: Preprocessing
@@ -83,22 +83,50 @@ for cid, cnt in sorted_clusters:
 ```
  
 **Be conservative with background merging.** Only merge colors that are nearly identical to background AND heavily touch edges. Subtle features (like a gray band between two shapes) will be destroyed by aggressive merging. When in doubt, keep the color.
+
+## Step 3b: Structural Edge Map
+
+Use the seeing-images skill to create a reference edge map. This distinguishes real structural boundaries from gradient-transition artifacts during contour extraction.
+
+```python
+import sys
+sys.path.insert(0, '/mnt/skills/user/seeing-images/scripts')
+from see import edges
+
+edge_path = edges(source_path, threshold=50)
+edge_img = cv2.imread(edge_path, cv2.IMREAD_GRAYSCALE)
+edge_img = cv2.resize(edge_img, (w_orig, h_orig))
+```
  
-## Step 4: Contour Extraction
- 
-For each non-background color cluster, extract filled contours:
+## Step 4: Contour Extraction (Boundary-Aware)
+
+The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Two mechanisms prevent this.
+
+For each non-background color cluster:
  
 ```python
+DARK_LUM_THRESHOLD = 55  # Luminance below this = "dark cluster"
+k_morph = np.ones((3,3), np.uint8)
+k_dilate = np.ones((3,3), np.uint8)  # MUST be 3x3. 5x5 causes blotchy artifacts.
+
 for cid, cnt in sorted_clusters:
     if cid in bg_clusters:
         continue
     
+    c = centers[cid]
+    lum = 0.299*c[0] + 0.587*c[1] + 0.114*c[2]
+    is_dark = lum < DARK_LUM_THRESHOLD
+    
     mask = (label_img == cid).astype(np.uint8) * 255
     
+    # FIX 1: Dilate non-dark regions to fill boundary gaps
+    # Lighter regions grow ~1.5px, covering the dark artifact zones
+    if not is_dark:
+        mask = cv2.dilate(mask, k_dilate, iterations=1)
+    
     # Morphological cleanup
-    k = np.ones((3,3), np.uint8)
-    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
-    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k, iterations=1)
+    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_morph, iterations=2)
+    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k_morph, iterations=1)
     
     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
     
@@ -107,8 +135,23 @@ for cid, cnt in sorted_clusters:
         if area < 40:
             continue
         
+        peri = cv2.arcLength(contour, True)
+        compactness = (4 * 3.14159 * area / (peri * peri)) if peri > 0 else 1
+        
+        # FIX 2: Gate dark shapes — keep real features, skip boundary artifacts
+        if is_dark:
+            contour_mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
+            cv2.drawContours(contour_mask, [contour], -1, 255, -1)
+            edge_overlap = cv2.bitwise_and(edge_img, contour_mask)
+            edge_density = edge_overlap.sum() / max(contour_mask.sum(), 1)
+            
+            # Keep if: compact (real dark area), edge-aligned, or large
+            if not (compactness > 0.15 or edge_density > 0.3
+                    or area > (h_orig * w_orig * 0.01)):
+                continue  # Skip: thin dark boundary artifact
+        
         # Simplify contour to reduce SVG path complexity
-        eps = 0.002 * cv2.arcLength(contour, True)
+        eps = 0.002 * peri
         approx = cv2.approxPolyDP(contour, eps, True)
         
         # Convert to SVG path (simple polygon — smallest file size)
@@ -121,6 +164,14 @@ for cid, cnt in sorted_clusters:
             path_d += f" L {p[0]:.1f},{p[1]:.1f}"
         path_d += " Z"
 ```
+
+**Why this works**: Boundary artifacts are thin (low compactness) AND don't correspond to real structural edges. Real dark features (eyes, hair, outlines in graphic art) have compact shapes or align with Sobel-detected edges.
+
+**Tuning**:
+- `DARK_LUM_THRESHOLD`: 55 works broadly; lower for dark images, higher for bright
+- Dilation kernel: 3×3 is the sweet spot. **Do NOT use 5×5** — causes blotchy artifacts in hair/foliage.
+- `compactness > 0.15`: Keeps circles/squares, filters ribbons
+- `edge_density > 0.3`: Keeps shapes aligned with real structural edges
  
 ## Step 5: Z-Ordering (Painter's Algorithm)
  
@@ -216,6 +267,8 @@ comparison.save('comparison.png')
 6. **Never aggressively merge near-background colors.** Subtle features live in these clusters. Only merge colors that are <10 RGB distance from background AND heavily touch image edges.
  
 7. **Don't use bezier smoothing unless specifically requested.** Simple L (line-to) polygons produce smaller SVGs. Bezier C commands triple the coordinate count per segment.
+
+8. **Don't use a dilation kernel larger than 3×3.** 5×5 was tested and causes blotchy artifacts in fine-detail areas like hair and foliage.
  
 ## File Size Guidelines
  
@@ -230,3 +283,5 @@ comparison.save('comparison.png')
 pip install opencv-python-headless scikit-image scipy --break-system-packages
 apt-get install -y librsvg2-bin  # for rsvg-convert
 ```
+
+**Cross-skill dependency**: [seeing-images](/mnt/skills/user/seeing-images/SKILL.md) — the `edges()` function is used in Step 3b for structural edge detection.
PATCH

echo "Gold patch applied."
