#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "**Tradeoffs**: K=64 on the Mona Lisa produces ~2300 shapes (~1.2MB SVG) vs K=32'" "image-to-svg/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/image-to-svg/SKILL.md b/image-to-svg/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: image-to-svg
-version: 1.2.0
+version: 1.3.0
 description: Convert raster images (photos, paintings, illustrations) into SVG vector reproductions. Use when the user uploads an image and asks to reproduce, vectorize, trace, or convert it to SVG. Also use when asked to decompose an image into shapes, create an SVG version of a picture, or faithfully reproduce artwork as vector graphics. Do NOT use for creating original SVG illustrations from text descriptions — only for converting existing raster images.
 ---
  
@@ -37,23 +37,41 @@ blurred = cv2.GaussianBlur(blurred, (3, 3), 0)
 **Do NOT boost saturation during preprocessing.** This distorts colors away from the original. Color correction, if needed, should be done as a final targeted step.
  
 ## Step 2: Color Quantization (K-means)
+
+**Before running quantization, choose K based on the image:**
+
+| Image type | K | Rationale |
+|-----------|---|-----------|
+| Photo — portrait, landscape, still life | 56–64 | Smooth tonal gradation matters. Faces need many skin tone steps. |
+| Painting — Renaissance, Impressionist, watercolor | 48–64 | Sfumato, blending, atmospheric perspective all need tonal range. |
+| Illustration — comics, editorial, digital art | 36–48 | Moderate palette, some gradation in shading. |
+| Graphic art — logos, icons, Kandinsky, flat design | 24–32 | Flat fills ARE the correct representation. More K adds noise. |
+| Pixel art, posterized, limited palette | 8–16 | Match the source palette. |
+
+When uncertain, **look at the image** and ask: "Does this have smooth gradients or hard edges?" Gradients → higher K. Hard edges → lower K. Default to 48 if unsure.
  
 ```python
 # Downscale for fast K-means, then apply centers to full resolution
 small = cv2.resize(blurred, (600, 390))
 pixels = small.reshape(-1, 3).astype(np.float32)
  
-K = 28–36  # More K = finer color separation, but more noise
-criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 150, 0.1)
-_, labels, centers = cv2.kmeans(pixels, K, None, criteria, 8, cv2.KMEANS_PP_CENTERS)
+# K chosen by image type — see table above
+criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
+_, labels, centers = cv2.kmeans(pixels, K, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
 centers = centers.astype(np.uint8)
  
-# Apply centers to full-res image
+# Apply centers to full-res image (batched to avoid memory issues at high K)
 full_px = blurred.reshape(-1, 3).astype(np.float32)
-dists = np.linalg.norm(full_px[:, None, :] - centers[None, :, :].astype(np.float32), axis=2)
-full_labels = np.argmin(dists, axis=1)
+batch_size = 50000
+full_labels = np.empty(len(full_px), dtype=np.int32)
+for i in range(0, len(full_px), batch_size):
+    chunk = full_px[i:i+batch_size]
+    dists = np.linalg.norm(chunk[:, None, :] - centers[None, :, :].astype(np.float32), axis=2)
+    full_labels[i:i+batch_size] = np.argmin(dists, axis=1)
 ```
- 
+
+**Tradeoffs**: K=64 on the Mona Lisa produces ~2300 shapes (~1.2MB SVG) vs K=32's ~1000 shapes (~550KB). Processing time roughly doubles. The quality gain in tonal gradation is substantial for photos and paintings but wasted on graphic art.
+
 **Save and inspect the quantized image** before proceeding. It represents the ceiling of what the SVG can achieve.
  
 ## Step 3: Background Detection
@@ -100,12 +118,26 @@ edge_img = cv2.resize(edge_img, (w_orig, h_orig))
  
 ## Step 4: Contour Extraction (Boundary-Aware)
 
-The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Two mechanisms prevent this.
+The standard K-means + contour pipeline creates "woodcut" artifacts: thin dark shapes at color boundaries where gradient transitions get quantized into separate dark clusters. Three mechanisms prevent this.
+
+First, build a dark territory mask — the union of all dark cluster pixels. This prevents non-dark dilation from encroaching on legitimate dark features (hair, dark clothing):
 
-For each non-background color cluster:
- 
 ```python
 DARK_LUM_THRESHOLD = 55  # Luminance below this = "dark cluster"
+
+dark_territory = np.zeros((h_orig, w_orig), dtype=np.uint8)
+for cid, cnt in sorted_clusters:
+    if cid in bg_clusters:
+        continue
+    c = centers[cid]
+    lum = 0.299*c[0] + 0.587*c[1] + 0.114*c[2]
+    if lum < DARK_LUM_THRESHOLD:
+        dark_territory[label_img == cid] = 255
+```
+
+Then extract contours per cluster:
+ 
+```python
 k_morph = np.ones((3,3), np.uint8)
 k_dilate = np.ones((3,3), np.uint8)  # MUST be 3x3. 5x5 causes blotchy artifacts.
 
@@ -119,10 +151,13 @@ for cid, cnt in sorted_clusters:
     
     mask = (label_img == cid).astype(np.uint8) * 255
     
-    # FIX 1: Dilate non-dark regions to fill boundary gaps
-    # Lighter regions grow ~1.5px, covering the dark artifact zones
+    # FIX 1: Dilate non-dark regions to fill boundary gaps, but respect dark territory
+    # Without the territory mask, background colors eat into hair/dark edges
     if not is_dark:
-        mask = cv2.dilate(mask, k_dilate, iterations=1)
+        dilated = cv2.dilate(mask, k_dilate, iterations=1)
+        growth = dilated & ~mask                    # new pixels from dilation
+        growth_into_dark = growth & dark_territory  # growth that would invade dark areas
+        mask = dilated & ~growth_into_dark           # keep growth only into non-dark gaps
     
     # Morphological cleanup
     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_morph, iterations=2)
@@ -149,6 +184,15 @@ for cid, cnt in sorted_clusters:
             if not (compactness > 0.08 or edge_density > 0.15
                     or area > (h_orig * w_orig * 0.01)):
                 continue  # Skip: thin dark boundary artifact
+            
+            # FIX 3: Isolation filter — small dark shapes surrounded by non-dark
+            # regions are artifacts, not features. Real dark features (eyes, hair)
+            # have dark neighbors.
+            if area < 500:
+                border = cv2.dilate(contour_mask, np.ones((11,11), np.uint8), 1) & ~contour_mask
+                border_dark = cv2.bitwise_and(dark_territory, border)
+                if border_dark.sum() / max(border.sum(), 1) < 0.3:
+                    continue  # Skip: isolated dark fragment
         
         # Simplify contour to reduce SVG path complexity
         eps = 0.002 * peri
@@ -165,7 +209,11 @@ for cid, cnt in sorted_clusters:
         path_d += " Z"
 ```
 
-**Why this works**: Boundary artifacts are thin (low compactness) AND don't correspond to real structural edges. Real dark features (eyes, hair, outlines in graphic art) have compact shapes or align with Sobel-detected edges.
+**Why this works**: Four mechanisms cooperate:
+1. **Dilation** fills dark boundary gaps between non-dark regions (the main woodcut fix)
+2. **Dark territory mask** prevents dilation from eating into real dark features like hair and clothing, which would create artificially sharp cutout edges
+3. **Dark shape gating** filters the remaining thin dark artifacts that aren't covered by dilation
+4. **Isolation filter** removes small dark shapes (<500px) that are surrounded by non-dark territory (dark_ratio < 0.3). At higher K, more boundary artifacts appear as isolated dark fragments in light regions
 
 **Tuning**:
 - `DARK_LUM_THRESHOLD`: 55 works broadly; lower for dark images, higher for bright
@@ -187,7 +235,7 @@ This naturally handles layering: large background elements go behind small foreg
 1. Red ring (largest)
 2. Any transition band (middle) — AFTER the ring so it paints ON TOP
 3. Black center (smallest) — AFTER everything so it covers the inner area
- 
+
 ## Step 6: SVG Assembly
  
 ```python
@@ -274,7 +322,8 @@ comparison.save('comparison.png')
  
 - Simple polygons (`M ... L ... L ... Z`): ~2 bytes per coordinate
 - Bezier curves (`C c1x,c1y c2x,c2y x,y`): ~6 bytes per coordinate  
-- Target: 500-1000 paths for a complex image, 400-900KB SVG
+- K=32: ~500-1000 paths, 400-600KB SVG
+- K=48–64: ~1500-2500 paths, 800KB-1.2MB SVG (recommended for photos/paintings)
 - Use `approxPolyDP` with epsilon ~0.002 * arc_length for good quality/size tradeoff
  
 ## Dependencies
PATCH

echo "Gold patch applied."
