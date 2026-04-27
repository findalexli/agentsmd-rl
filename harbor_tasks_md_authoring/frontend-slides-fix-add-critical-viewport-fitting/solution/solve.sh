#!/usr/bin/env bash
set -euo pipefail

cd /workspace/frontend-slides

# Idempotency guard
if grep -qF "- **When adding images to existing slides:** Move image to new slide or reduce o" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -228,12 +228,14 @@ If you find yourself with too much content:
 - Shorten text (aim for 1-2 lines per bullet)
 - Use smaller code snippets
 - Create a "continued" slide
+- **When adding images to existing slides:** Move image to new slide or reduce other content first
 
 **DON'T:**
 - Reduce font size below readable limits
 - Remove padding/spacing entirely
 - Allow any scrolling
 - Cram content to fit
+- Add images without checking if existing content already fills the viewport
 
 ### Testing Viewport Fit
 
@@ -260,6 +262,53 @@ First, determine what the user wants:
 **Mode C: Existing Presentation Enhancement**
 - User has an HTML presentation and wants to improve it
 - Read the existing file, understand the structure, then enhance
+- **CRITICAL: When modifying existing slides, ALWAYS ensure viewport fitting is maintained**
+
+### Mode C: Critical Modification Rules
+
+When enhancing existing presentations, follow these mandatory rules:
+
+**1. Before Adding Any Content:**
+- Read the current slide structure and count existing elements
+- Check against content density limits (see table above)
+- Calculate if the new content will fit within viewport constraints
+
+**2. When Adding Images (MOST COMMON ISSUE):**
+- Images must have `max-height: min(50vh, 400px)` or similar viewport constraint
+- Check if current slide already has maximum content (1 heading + 1 image)
+- If adding an image to a slide with existing content → **Split into two slides**
+- Example: If slide has heading + 4 bullets, and user wants to add an image:
+  - **DON'T:** Cram image onto same slide
+  - **DO:** Create new slide with heading + image, keep bullets on original slide
+  - **OR:** Reduce bullets to 2-3 and add image with proper constraints
+
+**3. When Adding Text Content:**
+- Max 4-6 bullet points per slide
+- Max 2 paragraphs per slide
+- If adding content exceeds limits → **Split into multiple slides or create a continuation slide**
+
+**4. Required Checks After ANY Modification:**
+```
+✅ Does the slide have `overflow: hidden` on `.slide` class?
+✅ Are all new elements using `clamp()` for font sizes?
+✅ Do new images have viewport-relative max-height?
+✅ Does total content respect density limits?
+✅ Will this fit on a 1280×720 screen? On mobile portrait?
+```
+
+**5. Proactive Reorganization (NOT Optional):**
+When you detect that modifications will cause overflow:
+- **Automatically split content across slides** — Don't wait for user to ask
+- Inform user: "I've reorganized the content across 2 slides to ensure proper viewport fitting"
+- Use "continued" pattern for split content (e.g., "Key Features" → "Key Features (Continued)")
+
+**6. Testing After Modifications:**
+Mentally verify the modified slide at these viewport sizes:
+- Desktop: 1280×720 (smallest common)
+- Tablet portrait: 768×1024
+- Mobile: 375×667
+
+**If in doubt → Split the content. Never allow scrolling within a slide.**
 
 ---
 
PATCH

echo "Gold patch applied."
