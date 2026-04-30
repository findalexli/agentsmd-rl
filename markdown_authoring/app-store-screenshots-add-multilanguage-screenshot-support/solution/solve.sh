#!/usr/bin/env bash
set -euo pipefail

cd /workspace/app-store-screenshots

# Idempotency guard
if grep -qF "10. **Localized screenshots** \u2014 \"Do you want screenshots in multiple languages? " "skills/app-store-screenshots/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/app-store-screenshots/SKILL.md b/skills/app-store-screenshots/SKILL.md
@@ -31,7 +31,8 @@ Before writing ANY code, ask the user all of these. Do not proceed until you hav
 
 8. **iPad screenshots** — "Do you also have iPad screenshots? If so, we'll generate iPad App Store screenshots too (recommended for universal apps)."
 9. **Component assets** — "Do you have any UI element PNGs (cards, widgets, etc.) you want as floating decorations? If not, that's fine — we'll skip them."
-10. **Additional instructions** — "Any specific requirements, constraints, or preferences?"
+10. **Localized screenshots** — "Do you want screenshots in multiple languages? This helps your listing rank in regional App Stores even if your app is English-only. If yes: which languages? (e.g. en, de, es, pt, ja)"
+11. **Additional instructions** — "Any specific requirements, constraints, or preferences?"
 
 ### Derived from answers (do NOT ask — decide yourself)
 
@@ -102,8 +103,45 @@ project/
 
 **Note:** No iPad mockup PNG is needed — the iPad frame is rendered with CSS (see iPad Mockup Component below).
 
+**Multi-language:** nest screenshots under a locale folder per language. The generator switches the `base` path; all slide image srcs stay identical.
+
+```
+└── screenshots/
+    ├── en/
+    │   ├── home.png
+    │   ├── feature-1.png
+    │   └── ...
+    ├── de/
+    │   └── ...
+    └── {locale}/
+```
+
 **The entire generator is a single `page.tsx` file.** No routing, no extra layouts, no API routes.
 
+### Multi-language: Locale Tabs
+
+Add a `LOCALES` array and locale tabs to the toolbar. Every slide src uses `base` — no hardcoded paths:
+
+```tsx
+const LOCALES = ["en", "de", "es"] as const; // use whatever langs were defined
+type Locale = typeof LOCALES[number];
+
+// In ScreenshotsPage:
+const [locale, setLocale] = useState<Locale>("en");
+const base = `/screenshots/${locale}`;
+
+// Toolbar tabs:
+{LOCALES.map(l => (
+  <button key={l} onClick={() => setLocale(l)}
+    style={{ fontWeight: locale === l ? 700 : 400 }}>
+    {l.toUpperCase()}
+  </button>
+))}
+
+// In every slide — unchanged between single and multi-language:
+<Phone src={`${base}/home.png`} alt="Home" />
+```
+
 ### Font Setup
 
 ```tsx
PATCH

echo "Gold patch applied."
