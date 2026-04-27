#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "**Generate a custom script when**: the operation needs logic `img-process` doesn" "plugins/design-assets/skills/image-processing/SKILL.md" && grep -qF "**c. \"How It Works\" flow** \u2014 the main workflow in sequence. Run `capture-screens" "plugins/frontend/skills/product-showcase/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/design-assets/skills/image-processing/SKILL.md b/plugins/design-assets/skills/image-processing/SKILL.md
@@ -6,11 +6,27 @@ compatibility: claude-code-only
 
 # Image Processing
 
-Process images for web development. Generate a Pillow script adapted to the user's environment and specific needs.
+Use `img-process` (shipped in `bin/`) for common operations. For complex or custom workflows, generate a Pillow script adapted to the user's environment.
+
+## Quick Reference — img-process CLI
+
+```bash
+img-process resize hero.png --width 1920
+img-process convert logo.png --format webp
+img-process trim logo-raw.jpg -o logo-clean.png --padding 10
+img-process thumbnail photo.jpg --size 200
+img-process optimise hero.jpg --quality 85 --max-width 1920
+img-process og-card -o og.png --title "My App" --subtitle "Built for speed"
+img-process batch ./images --action convert --format webp -o ./optimised
+```
+
+**Use `img-process` when**: the operation is standard (resize, convert, trim, thumbnail, optimise, OG card, batch). This is faster and avoids generating a script each time.
+
+**Generate a custom script when**: the operation needs logic `img-process` doesn't cover (compositing multiple images, watermarks, complex text layouts, conditional processing).
 
 ## Prerequisites
 
-Pillow is usually pre-installed. If not:
+Pillow is required for both `img-process` and custom scripts:
 
 ```bash
 pip install Pillow
@@ -24,12 +40,6 @@ If Pillow is unavailable, use alternatives:
 | `sharp` | Node.js | `npm install sharp` | Full feature set, high performance |
 | `ffmpeg` | Cross-platform | `brew install ffmpeg` | Resize, convert |
 
-```bash
-# macOS sips examples
-sips --resampleWidth 1920 input.jpg --out resized.jpg
-sips --setProperty format webp input.jpg --out output.webp
-```
-
 ## Output Format Guide
 
 | Use case | Format | Why |
@@ -176,22 +186,32 @@ img = img.convert("RGB")
 
 ### Logo Cleanup (client-supplied JPG with white background)
 
-1. Trim whitespace
-2. Convert to PNG (for transparency)
-3. Create favicon-sized version (thumbnail at 512px)
+```bash
+img-process trim logo-raw.jpg -o logo-trimmed.png --padding 10
+img-process thumbnail logo-trimmed.png --size 512 -o favicon-512.png
+```
 
 ### Prepare Hero Image for Production
 
-Resize to max width 1920, convert to WebP, compress at quality 85.
+```bash
+img-process optimise hero.jpg --max-width 1920 --quality 85
+# Outputs hero.webp — resized and compressed
+```
 
 ### Batch Process
 
-For multiple images, generate a single script that loops over all files rather than processing one at a time.
+```bash
+img-process batch ./raw-images --action convert --format webp --quality 85 -o ./optimised
+img-process batch ./photos --action resize --width 800 -o ./thumbnails
+```
 
-## Pipeline with Gemini Image Gen
+### Pipeline with Gemini Image Gen
 
 Generate images with the gemini-image-gen skill, then process them:
 
-1. Generate with Gemini (raw PNG output)
-2. User picks favourite
-3. Optimise: resize to target width, convert to WebP, compress
+```bash
+# After generating with Gemini (raw PNG output):
+img-process optimise generated-image.png --max-width 1920 --quality 85
+# Or batch process all generated images:
+img-process batch ./generated --action optimise -o ./production
+```
diff --git a/plugins/frontend/skills/product-showcase/SKILL.md b/plugins/frontend/skills/product-showcase/SKILL.md
@@ -42,36 +42,46 @@ Before starting, detect available browser tools:
 | CTA text + URL | No | "Start Free Trial" → signup page |
 | Testimonials | No | User provides or skip section |
 
-### 2. Explore the App
+### 2. Capture Screenshots
 
-Navigate the app and capture the story:
+Use `capture-screenshots` (shipped in `bin/`) to capture the app. This is faster and more consistent than generating Playwright scripts each time.
 
-#### a. First Impression
-- Load the app's main page/dashboard
-- Screenshot at 1280x720 — this becomes the hero image
-- Note the immediate value proposition (what does the user see first?)
+#### Quick capture (all key pages at once):
+```bash
+capture-screenshots http://localhost:5173 \
+  --pages /,/dashboard,/contacts,/settings \
+  --output showcase/screenshots \
+  --prefix screen \
+  --mobile --dark
+```
+
+This produces desktop (1280x720), mobile (375px), and dark mode variants for each page in one run.
+
+#### For authenticated apps:
+```bash
+capture-screenshots https://app.example.com \
+  --pages /,/dashboard,/settings \
+  --auth user:password \
+  --output showcase/screenshots \
+  --mobile --dark
+```
+
+#### What to capture:
 
-#### b. Discover Features
-Navigate through each major section:
-- Click every nav item, tab, and major UI element
-- For each feature area, take a clean screenshot showing it in action
-- Note what the user can DO (actions, not just views)
-- Capture 6-10 key screens that tell the product story
+**a. First Impression** — the main page/dashboard becomes the hero image. Note the immediate value proposition.
 
-#### c. Identify the "How It Works" Flow
-Find the main workflow (the thing a user does most):
-- Screenshot 3-4 steps in sequence
-- These become the "How It Works" section
-- Example: "1. Add a contact → 2. Set up a pipeline → 3. Track your deals → 4. See your dashboard"
+**b. Features** — each major section. Use `--pages` with all nav paths. Capture 6-10 key screens that tell the product story.
 
-#### d. Capture Detail Shots
-For the feature grid, capture focused screenshots:
-- Zoom into specific UI elements that showcase polish
-- Dark mode version if available (shows design quality)
-- Mobile view if the app is responsive
+**c. "How It Works" flow** — the main workflow in sequence. Run `capture-screenshots` multiple times with `--prefix workflow-step` as you navigate through the flow steps.
 
-#### e. Capture Both Modes
-If the app has dark mode, capture the hero and 2-3 key screens in both light and dark. Use the best-looking mode for the hero, show the other in a "Works in dark mode too" section or as a side-by-side comparison.
+**d. Detail shots** — zoom into specific UI elements. Use `--full-page` for scrollable content.
+
+**e. Both modes** — `--dark` flag captures light and dark variants automatically. Use the best-looking mode for the hero.
+
+#### Post-capture optimisation:
+```bash
+img-process batch showcase/screenshots --action optimise --max-width 1920 -o showcase/screenshots-opt
+```
 
 #### f. Extract the Value Propositions
 Don't just list features. For each one, answer: **why does the user care?**
@@ -155,18 +165,22 @@ Static screenshots don't convey workflow. For key features, capture animated GIF
 4. Stop recording
 5. Combine frames into a GIF
 
-**Generating the GIF** (Python script):
-```python
-from PIL import Image
-import glob
-
-frames = []
-for f in sorted(glob.glob('.jez/screenshots/workflow-*.png')):
-    frames.append(Image.open(f))
-
+**Generating the GIF** — capture sequential screenshots then combine:
+```bash
+# Capture each step with a sequential prefix
+capture-screenshots http://localhost:5173/clients \
+  --prefix workflow-01 --output .jez/screenshots
+# ... navigate to next state ...
+capture-screenshots http://localhost:5173/clients/new \
+  --prefix workflow-02 --output .jez/screenshots
+
+# Combine frames into GIF (Python one-liner using Pillow)
+python3 -c "
+from PIL import Image; import glob
+frames = [Image.open(f) for f in sorted(glob.glob('.jez/screenshots/workflow-*.png'))]
 frames[0].save('showcase/screenshots/workflows/create-client.gif',
-    save_all=True, append_images=frames[1:],
-    duration=500, loop=0)  # 500ms per frame
+    save_all=True, append_images=frames[1:], duration=500, loop=0)
+"
 ```
 
 **What to animate**:
PATCH

echo "Gold patch applied."
