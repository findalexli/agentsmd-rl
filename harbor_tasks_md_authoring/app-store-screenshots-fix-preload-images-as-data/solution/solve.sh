#!/usr/bin/env bash
set -euo pipefail

cd /workspace/app-store-screenshots

# Idempotency guard
if grep -qF "`html-to-image` works by cloning the DOM into an SVG `<foreignObject>`, then pai" "skills/app-store-screenshots/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/app-store-screenshots/SKILL.md b/skills/app-store-screenshots/SKILL.md
@@ -532,6 +532,65 @@ Dark/contrast background with app icon, headline ("And so much more."), and feat
 
 `html2canvas` breaks on CSS filters, gradients, drop-shadow, backdrop-filter, and complex clipping. `html-to-image` uses native browser SVG serialization — handles all CSS faithfully.
 
+### Pre-load Images as Data URIs (CRITICAL)
+
+`html-to-image` works by cloning the DOM into an SVG `<foreignObject>`, then painting it to a canvas. During cloning, it re-fetches every `<img>` src. These re-fetches are non-deterministic — some hit the browser cache, some silently fail. Failed images render as transparent rectangles in the export (black after alpha flattening).
+
+**The fix: pre-convert all images to base64 data URIs at page load and use those as `src` everywhere.** When `html-to-image` clones the DOM, data URI sources are already inline — no fetch needed.
+
+```typescript
+// At module level — list all image paths used in slides
+const IMAGE_PATHS = [
+  "/mockup.png",
+  "/app-icon.png",
+  "/screenshots/home.png",
+  "/screenshots/feature-1.png",
+  // ... all images used in any slide
+];
+
+const imageCache: Record<string, string> = {};
+
+async function preloadAllImages() {
+  await Promise.all(
+    IMAGE_PATHS.map(async (path) => {
+      const resp = await fetch(path);
+      const blob = await resp.blob();
+      const dataUrl = await new Promise<string>((resolve) => {
+        const reader = new FileReader();
+        reader.onloadend = () => resolve(reader.result as string);
+        reader.readAsDataURL(blob);
+      });
+      imageCache[path] = dataUrl;
+    })
+  );
+}
+
+// Helper — use in every <img> src
+function img(path: string): string {
+  return imageCache[path] || path;
+}
+```
+
+In the page component, gate rendering on preload completion:
+
+```typescript
+const [ready, setReady] = useState(false);
+useEffect(() => { preloadAllImages().then(() => setReady(true)); }, []);
+if (!ready) return <p>Loading images...</p>;
+```
+
+In every slide component, use `img()` instead of raw paths:
+
+```tsx
+// Before (breaks non-deterministically):
+<img src="/screenshots/home.png" />
+
+// After (always works):
+<img src={img("/screenshots/home.png")} />
+```
+
+**Also flatten RGBA source images to RGB before use.** If your app screenshots are RGBA PNGs, `html-to-image` can fail to serialize them. Convert source images to RGB (no alpha) before placing them in `public/screenshots/`.
+
 ### Export Implementation
 
 ```typescript
@@ -597,6 +656,8 @@ At minimum, support:
 - 300ms delay between sequential exports.
 - Set `fontFamily` on the offscreen container.
 - **Numbered filenames**: Prefix exports with zero-padded index so they sort correctly: `01-hero-1320x2868.png`, `02-freshness-1320x2868.png`, etc. Use `String(index + 1).padStart(2, "0")`.
+- **Pre-loaded data URIs**: Always use the `img()` helper with pre-loaded base64 data URIs for all `<img>` sources. Never use raw file paths in slide components — `html-to-image` will fail to capture them non-deterministically.
+- **RGB source images**: Ensure all source screenshots in `public/screenshots/` are RGB (not RGBA). RGBA PNGs can fail during SVG serialization and produce transparent/black regions in exports.
 
 ## Step 7: Final QA Gate
 
@@ -645,3 +706,6 @@ When you present the finished work:
 | Headlines use "and" | Split into two slides or pick one idea |
 | No visual contrast across slides | Mix light and dark backgrounds |
 | Export is blank | Use double-call trick; move element on-screen before capture |
+| Phone screens black/empty in export but visible in preview | Images not inlined — use `preloadAllImages()` + `img()` helper so all `<img>` src attributes are base64 data URIs before `toPng` runs |
+| Some slides export correctly, others have missing images | Non-deterministic `html-to-image` fetch race condition — same root cause as above, fix with pre-loaded data URIs |
+| Screenshots rejected by App Store with IMAGE_ALPHA_NOT_ALLOWED | Source PNGs have alpha channel — flatten to RGB before use (composite onto black with PIL or remove alpha in your image editor) |
PATCH

echo "Gold patch applied."
