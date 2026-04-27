#!/usr/bin/env bash
set -euo pipefail

cd /workspace/frontend-slides

# Idempotency guard
if grep -qF "**Logo in previews (if available):** If the user provided images in Step 1.2 and" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -267,7 +267,9 @@ First, determine what the user wants:
 
 Before designing, understand the content. Ask via AskUserQuestion:
 
-### Step 1.1: Presentation Context
+### Step 1.1: Presentation Context + Images (Single Form)
+
+**IMPORTANT:** Ask ALL 4 questions in a single AskUserQuestion call so the user can fill everything out at once before submitting.
 
 **Question 1: Purpose**
 - Header: "Purpose"
@@ -294,8 +296,59 @@ Before designing, understand the content. Ask via AskUserQuestion:
   - "I have rough notes" — Need help organizing into slides
   - "I have a topic only" — Need help creating the full outline
 
+**Question 4: Images**
+- Header: "Images"
+- Question: "Do you have images to include? Select 'No images' or select Other and type/paste your image folder path."
+- Options:
+  - "No images" — Text-only presentation (use CSS-generated visuals instead)
+  - "./assets" — Use the `assets/` folder in the current project
+
+The user can select **"Other"** to type or paste any custom folder path (e.g. `~/Desktop/screenshots`). This way the image folder path is collected in the same form — no extra round-trip.
+
 If user has content, ask them to share it (text, bullet points, images, etc.).
 
+### Step 1.2: Image Evaluation
+
+**User-provided assets are important visual anchors** — but not every asset is necessarily usable. The first step is always to evaluate. After evaluation, the curated assets become additional context that shapes how the presentation is built. This is a **co-design process**: text content + curated visuals together inform the slide structure from the start, not a post-hoc "fit images in after the fact."
+
+**If user selected "No images"** → Skip the entire image pipeline. Proceed directly to Phase 2 (Style Discovery) and Phase 3 (Generate Presentation) using text content only. The presentation will use CSS-generated visuals (gradients, shapes, patterns, typography) for visual interest — this is the original behavior and produces fully polished results without any images.
+
+**If user provides an image folder:**
+
+1. **Scan the folder** — Use `ls` to list all image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`)
+2. **View each image** — Use the Read tool to see what each image contains (Claude is multimodal)
+3. **Evaluate each image** — For each image, assess:
+   - Filename and dimensions
+   - What it shows (screenshot, logo, chart, diagram, photo)
+   - **Usability:** Is the image clear, relevant to the presentation topic, and high enough quality? Mark as `USABLE` or `NOT USABLE` (with reason: blurry, irrelevant, broken, etc.)
+   - **Content signal:** What feature or concept does this image represent? (e.g., "chat_ui.png" → "conversational interface feature")
+   - Shape: square, landscape, portrait, circular
+   - Dominant colors (important for style compatibility later)
+4. **Present the evaluation and proposed slide outline to the user** — Show which images are usable and which are not, with reasons. Then show the proposed slide outline with image assignments.
+
+**Co-design: curated assets inform the outline**
+
+After evaluation, the **usable** images become context for planning the slide structure alongside text content. This is not "plan slides then add images" — it's designing the presentation around both text and visuals from the start:
+
+- 3 usable product screenshots → plan 3 feature slides, each anchored by one screenshot
+- 1 usable logo → title slide and/or closing slide
+- 1 usable architecture diagram → dedicated "How It Works" slide
+- 1 blurry/irrelevant image → excluded, with explanation to user
+
+This means curated images are factored in **before** style selection (Phase 2) and **before** HTML generation (Phase 3). They are co-equal context in the design process.
+
+5. **Confirm outline via AskUserQuestion** — Do NOT break the flow by asking the user to type free text. Use AskUserQuestion to confirm:
+
+**Question: Outline Confirmation**
+- Header: "Outline"
+- Question: "Does this slide outline and image selection look right?"
+- Options:
+  - "Looks good, proceed" — Move on to style selection
+  - "Adjust images" — I want to change which images go where
+  - "Adjust outline" — I want to change the slide structure
+
+This keeps the entire flow in the AskUserQuestion format without dropping to free-text chat.
+
 ---
 
 ## Phase 2: Style Discovery (Visual Exploration)
@@ -421,6 +474,8 @@ Each preview file should be:
 - Animated to demonstrate motion style
 - ~50-100 lines, not a full presentation
 
+**Logo in previews (if available):** If the user provided images in Step 1.2 and a logo was identified as `USABLE`, embed it (base64) into each of the 3 style previews. This creates a "wow moment" — the user sees their own brand identity styled three different ways, making the choice feel personal rather than abstract. Apply any necessary processing (e.g., circular crop) per-style so each preview shows the logo as it would actually appear in the final presentation. If no logo was provided, generate previews without one — this is fine.
+
 Present to user:
 ```
 I've created 3 style previews for you to compare:
@@ -458,9 +513,132 @@ If "Mix elements", ask for specifics.
 ## Phase 3: Generate Presentation
 
 Now generate the full presentation based on:
-- Content from Phase 1
+- Content from Phase 1 (text only, or text + curated images)
 - Style from Phase 2
 
+If the user provided images, the slide outline already incorporates them as visual anchors from Step 1.2. If not, proceed with text-only content — CSS-generated visuals (gradients, shapes, patterns) provide visual interest.
+
+### Image Pipeline (skip if no images)
+
+If the user chose "No images" in Step 1.2, **skip this entire section** and go straight to generating HTML. The presentation will be text-only with CSS-generated visuals — this is a fully supported, first-class path.
+
+If the user provided images, execute these steps **before** generating HTML.
+
+**Key principle: Co-design, not post-hoc.** The curated images from Step 1.2 (those marked `USABLE`) are already part of the slide outline. The pipeline's job here is to process images for the chosen style and place them in the HTML.
+
+#### Step 3.1: Image Processing (Pillow)
+
+For each curated image, determine what processing it needs based on the chosen style (e.g., circular crop for logos, resize for large files) and what CSS framing will bridge any color gaps between the image and the style's palette. Then process accordingly.
+
+**Rules:**
+- **Never repeat** the same image on multiple slides (except logos which may bookend title + closing)
+- **Always add CSS framing** (border, glow, shadow) for images whose colors clash with the style's palette
+
+**Dependency:** Python `Pillow` library (the standard image processing library for Python).
+
+```bash
+# Install if not available (portable across macOS/Linux/Windows)
+pip install Pillow
+```
+
+This is analogous to how `python-pptx` is used in Phase 4 (PPT Conversion) — a standard, well-maintained Python package that any user can install.
+
+**Common processing operations:**
+
+```python
+from PIL import Image, ImageDraw
+
+# ─── Circular Crop (for logos on modern/clean styles) ───
+def crop_circle(input_path, output_path):
+    """Crop a square image to a circle with transparent background."""
+    img = Image.open(input_path).convert('RGBA')
+    w, h = img.size
+    # Make square if not already
+    size = min(w, h)
+    left = (w - size) // 2
+    top = (h - size) // 2
+    img = img.crop((left, top, left + size, top + size))
+    # Create circular mask
+    mask = Image.new('L', (size, size), 0)
+    draw = ImageDraw.Draw(mask)
+    draw.ellipse([0, 0, size, size], fill=255)
+    img.putalpha(mask)
+    img.save(output_path, 'PNG')
+
+# ─── Resize (for oversized images that inflate the HTML) ───
+def resize_max(input_path, output_path, max_dim=1200):
+    """Resize image so largest dimension <= max_dim. Preserves aspect ratio."""
+    img = Image.open(input_path)
+    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
+    img.save(output_path, quality=85)
+
+# ─── Add Padding / Background (for images that need breathing room) ───
+def add_padding(input_path, output_path, padding=40, bg_color=(0, 0, 0, 0)):
+    """Add transparent padding around an image."""
+    img = Image.open(input_path).convert('RGBA')
+    w, h = img.size
+    new = Image.new('RGBA', (w + 2*padding, h + 2*padding), bg_color)
+    new.paste(img, (padding, padding), img)
+    new.save(output_path, 'PNG')
+```
+
+**When to apply each operation:**
+
+| Situation | Operation |
+|-----------|-----------|
+| Square logo on a style with rounded aesthetics | `crop_circle()` |
+| Image > 1MB (slow to load) | `resize_max(max_dim=1200)` |
+| Screenshot needs breathing room in layout | `add_padding()` |
+| Image has wrong aspect ratio for its slide slot | Manual crop with `img.crop((left, top, right, bottom))` |
+
+**Save processed images** alongside originals with a `_processed` suffix (e.g., `logo_round.png`). Never overwrite the user's original files.
+
+#### Step 3.2: Place Images
+
+**Use direct file paths** — do NOT convert images to base64 data URIs. Since presentations are viewed locally, reference images with relative paths from the HTML file:
+
+```html
+<img src="assets/logo_round.png" alt="Logo" class="slide-image logo">
+<img src="assets/screenshot.png" alt="Screenshot" class="slide-image screenshot">
+```
+
+This keeps the HTML file small and images easy to swap. Only use base64 encoding if the user explicitly requests a fully self-contained single-file presentation.
+
+**Image CSS classes (adapt border/glow colors to match the chosen style):**
+```css
+/* Base image constraint — CRITICAL for viewport fitting */
+.slide-image {
+    max-width: 100%;
+    max-height: min(50vh, 400px);
+    object-fit: contain;
+    border-radius: 8px;
+}
+
+/* Screenshots: add framing to bridge color gaps with the style */
+.slide-image.screenshot {
+    border: 1px solid rgba(255, 255, 255, 0.1);
+    border-radius: 12px;
+    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
+}
+
+/* Logos: smaller, no frame */
+.slide-image.logo {
+    max-height: min(30vh, 200px);
+}
+```
+
+**IMPORTANT:** Adapt the `.screenshot` border and shadow colors to match the chosen style's accent color. For example:
+- Dark Botanical (gold accent): `border: 1px solid rgba(197, 160, 89, 0.2); box-shadow: 0 0 20px rgba(197, 160, 89, 0.08);`
+- Creative Voltage (neon yellow): `border: 2px solid rgba(212, 255, 0, 0.25); box-shadow: 0 0 20px rgba(212, 255, 0, 0.08);`
+
+**Placement patterns:**
+- **Title slide:** Logo centered above or beside the title
+- **Feature slides:** Screenshot on one side, text on the other (two-column layout)
+- **Full-bleed:** Image as slide background with text overlay (use with caution)
+- **Inline:** Image within content flow, centered, with caption below
+
+**Note:** Processed images (e.g. `logo_round.png`) are saved alongside originals in the assets folder. Reference them with relative paths in the HTML.
+
 ### File Structure
 
 For single presentations:
@@ -1077,15 +1255,22 @@ class TiltEffect {
 ## Example Session Flow
 
 1. User: "I want to create a pitch deck for my AI startup"
-2. Skill asks about purpose, length, content
-3. User shares their bullet points and key messages
-4. Skill asks about desired feeling (Impressed + Excited)
-5. Skill generates 3 style previews
-6. User picks Style B (Neon Cyber), asks for darker background
-7. Skill generates full presentation with all slides
-8. Skill opens the presentation in browser
-9. User requests tweaks to specific slides
-10. Final presentation delivered
+2. Skill asks about purpose, length, content, and images (single form)
+3. User shares bullet points, selects `./assets` folder
+4. **Evaluate:** Skill views each image (multimodal), builds slide outline with image assignments:
+   - `logo.png` → USABLE → title/closing slide
+   - `chat_ui.png` → USABLE → feature slide
+   - `dashboard.png` → USABLE → feature slide
+   - `launch_card.png` → USABLE → feature slide
+   - `blurry_team.jpg` → NOT USABLE (too low resolution)
+5. User confirms outline via AskUserQuestion
+6. Skill asks about desired feeling (Impressed + Excited)
+7. Skill generates 3 style previews
+8. User picks Style B (Neon Cyber)
+9. **Process + Generate:** Skill runs Pillow operations (circular crop, resize), generates full presentation with direct image paths
+10. Skill opens the presentation in browser
+11. User requests tweaks to specific slides
+12. Final presentation delivered
 
 ---
 
PATCH

echo "Gold patch applied."
