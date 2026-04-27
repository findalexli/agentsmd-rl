#!/usr/bin/env bash
set -euo pipefail

cd /workspace/app-store-screenshots

# Idempotency guard
if grep -qF "When supporting both devices, add a toggle (iPhone / iPad) in the toolbar next t" "skills/app-store-screenshots/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/app-store-screenshots/SKILL.md b/skills/app-store-screenshots/SKILL.md
@@ -29,8 +29,9 @@ Before writing ANY code, ask the user all of these. Do not proceed until you hav
 
 ### Optional
 
-8. **Component assets** — "Do you have any UI element PNGs (cards, widgets, etc.) you want as floating decorations? If not, that's fine — we'll skip them."
-9. **Additional instructions** — "Any specific requirements, constraints, or preferences?"
+8. **iPad screenshots** — "Do you also have iPad screenshots? If so, we'll generate iPad App Store screenshots too (recommended for universal apps)."
+9. **Component assets** — "Do you have any UI element PNGs (cards, widgets, etc.) you want as floating decorations? If not, that's fine — we'll skip them."
+10. **Additional instructions** — "Any specific requirements, constraints, or preferences?"
 
 ### Derived from answers (do NOT ask — decide yourself)
 
@@ -76,16 +77,20 @@ npm install html-to-image
 
 ### Copy the Phone Mockup
 
-The skill includes a pre-measured iPhone mockup at `mockup.png` (co-located with this SKILL.md). Copy it to the project's `public/` directory. The mockup file is in the same directory as this skill file.
+The skill includes a pre-measured iPhone mockup at `mockup.png` (co-located with this SKILL.md). Copy it to the project's `public/` directory. The mockup file is in the same directory as this skill file. No iPad mockup is needed — the iPad frame is CSS-only.
 
 ### File Structure
 
 ```
 project/
 ├── public/
-│   ├── mockup.png              # Phone frame (included with skill)
+│   ├── mockup.png              # iPhone frame (included with skill)
 │   ├── app-icon.png            # User's app icon
-│   └── screenshots/            # User's app screenshots
+│   ├── screenshots/            # iPhone app screenshots
+│   │   ├── home.png
+│   │   ├── feature-1.png
+│   │   └── ...
+│   └── screenshots-ipad/       # iPad app screenshots (optional)
 │       ├── home.png
 │       ├── feature-1.png
 │       └── ...
@@ -95,6 +100,8 @@ project/
 └── package.json
 ```
 
+**Note:** No iPad mockup PNG is needed — the iPad frame is rendered with CSS (see iPad Mockup Component below).
+
 **The entire generator is a single `page.tsx` file.** No routing, no extra layouts, no API routes.
 
 ### Font Setup
@@ -175,20 +182,24 @@ Get all headlines approved before building layouts. Bad copy ruins good design.
 
 ```
 page.tsx
-├── Constants (W, H, SIZES, design tokens from user's brand)
-├── Phone component (mockup with screen overlay)
-├── Caption component (label + headline)
+├── Constants (IPHONE_W/H, IPAD_W/H, SIZES, design tokens)
+├── Phone component (mockup PNG with screen overlay)
+├── IPad component (CSS-only frame with screen overlay)
+├── Caption component (label + headline, accepts canvasW for scaling)
 ├── Decorative components (blobs, glows, shapes — based on style direction)
-├── Screenshot1..N components (one per slide)
-├── SCREENSHOTS array (registry)
+├── iPhoneSlide1..N components (one per slide)
+├── iPadSlide1..N components (same designs, adjusted for iPad proportions)
+├── IPHONE_SCREENSHOTS / IPAD_SCREENSHOTS arrays (registries)
 ├── ScreenshotPreview (ResizeObserver scaling + hover export)
-└── ScreenshotsPage (grid + toolbar + export logic)
+└── ScreenshotsPage (grid + device toggle + size dropdown + export logic)
 ```
 
-### Export Sizes (Apple Required — iPhone only, portrait)
+### Export Sizes (Apple Required, portrait)
+
+#### iPhone
 
 ```typescript
-const SIZES = [
+const IPHONE_SIZES = [
   { label: '6.9"', w: 1320, h: 2868 },
   { label: '6.5"', w: 1284, h: 2778 },
   { label: '6.3"', w: 1206, h: 2622 },
@@ -198,6 +209,23 @@ const SIZES = [
 
 Design at the LARGEST size (1320x2868) and scale down for export.
 
+#### iPad (Optional)
+
+If the user provides iPad screenshots, also generate iPad App Store screenshots:
+
+```typescript
+const IPAD_SIZES = [
+  { label: '13" iPad', w: 2064, h: 2752 },
+  { label: '12.9" iPad Pro', w: 2048, h: 2732 },
+] as const;
+```
+
+Design iPad slides at 2064x2752 and scale down. iPad screenshots are optional but recommended — they're required for iPad-only apps and improve listing quality for universal apps.
+
+#### Device Toggle
+
+When supporting both devices, add a toggle (iPhone / iPad) in the toolbar next to the size dropdown. The size dropdown should switch between iPhone and iPad sizes based on the selected device. Support a `?device=ipad` URL parameter for headless/automated capture workflows.
+
 ### Rendering Strategy
 
 Each screenshot is designed at full resolution (1320x2868px). Two copies exist:
@@ -244,6 +272,61 @@ function Phone({ src, alt, style, className = "" }: {
 }
 ```
 
+### iPad Mockup Component (CSS-Only)
+
+Unlike the iPhone mockup which uses a pre-measured PNG frame, the iPad uses a **CSS-only frame**. This avoids needing a separate mockup asset and looks clean at any resolution.
+
+**Critical dimension:** The frame aspect ratio must be `770/1000` so the inner screen area (92% width × 94.4% height) matches the 3:4 aspect ratio of iPad screenshots. Using incorrect proportions causes black bars or stretched screenshots.
+
+```tsx
+function IPad({ src, alt, style, className = "" }: {
+  src: string; alt: string; style?: React.CSSProperties; className?: string;
+}) {
+  return (
+    <div className={`relative ${className}`}
+      style={{ aspectRatio: "770/1000", ...style }}>
+      <div style={{
+        width: "100%", height: "100%", borderRadius: "5% / 3.6%",
+        background: "linear-gradient(180deg, #2C2C2E 0%, #1C1C1E 100%)",
+        position: "relative", overflow: "hidden",
+        boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.1), 0 8px 40px rgba(0,0,0,0.6)",
+      }}>
+        {/* Front camera dot */}
+        <div style={{
+          position: "absolute", top: "1.2%", left: "50%",
+          transform: "translateX(-50%)", width: "0.9%", height: "0.65%",
+          borderRadius: "50%", background: "#111113",
+          border: "1px solid rgba(255,255,255,0.08)", zIndex: 20,
+        }} />
+        {/* Bezel edge highlight */}
+        <div style={{
+          position: "absolute", inset: 0, borderRadius: "5% / 3.6%",
+          border: "1px solid rgba(255,255,255,0.06)",
+          pointerEvents: "none", zIndex: 15,
+        }} />
+        {/* Screen area */}
+        <div style={{
+          position: "absolute", left: "4%", top: "2.8%",
+          width: "92%", height: "94.4%",
+          borderRadius: "2.2% / 1.6%", overflow: "hidden", background: "#000",
+        }}>
+          <img src={src} alt={alt}
+            style={{ display: "block", width: "100%", height: "100%",
+              objectFit: "cover", objectPosition: "top" }}
+            draggable={false} />
+        </div>
+      </div>
+    </div>
+  );
+}
+```
+
+**iPad layout adjustments vs iPhone:**
+- Use `width: "65-70%"` for iPad mockups (vs 82-86% for iPhone) — iPad is wider relative to its height
+- Two-iPad layouts work the same as two-phone layouts but with adjusted widths
+- Caption font sizes should scale from `canvasW` (which is 2064 for iPad vs 1320 for iPhone)
+- Same slide designs/copy can be reused — just swap the Phone component for IPad and adjust positioning
+
 ### Typography (Resolution-Independent)
 
 All sizing relative to canvas width W:
PATCH

echo "Gold patch applied."
