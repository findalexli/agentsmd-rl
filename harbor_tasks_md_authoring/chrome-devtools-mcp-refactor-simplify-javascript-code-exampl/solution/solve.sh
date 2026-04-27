#!/usr/bin/env bash
set -euo pipefail

cd /workspace/chrome-devtools-mcp

# Idempotency guard
if grep -qF "**Reading web.dev documentation**: If you need to research specific accessibilit" "skills/a11y-debugging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/a11y-debugging/SKILL.md b/skills/a11y-debugging/SKILL.md
@@ -7,7 +7,7 @@ description: Uses Chrome DevTools MCP for accessibility (a11y) debugging and aud
 
 **Accessibility Tree vs DOM**: Visually hiding an element (e.g., `CSS opacity: 0`) behaves differently for screen readers than `display: none` or `aria-hidden="true"`. The `take_snapshot` tool returns the accessibility tree of the page, which represents what assistive technologies "see", making it the most reliable source of truth for semantic structure.
 
-**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https://web.dev/articles/accessible-tap-targets.md.txt`) to fetch the clean, raw markdown version. This is much easier to read using the `read_url_content` tool!
+**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https://web.dev/articles/accessible-tap-targets.md.txt`) to fetch the clean, raw markdown version. This is much easier to read!
 
 ## Workflow Patterns
 
@@ -34,26 +34,21 @@ The accessibility tree exposes the heading hierarchy and semantic landmarks.
 1.  Locate buttons, inputs, and images in the `take_snapshot` output.
 2.  Ensure interactive elements have an accessible name (e.g., a button should not just say `""` if it only contains an icon).
 3.  **Orphaned Inputs**: Verify that all form inputs have associated labels. Use `evaluate_script` to check for inputs missing `id` (for `label[for]`) or `aria-label`:
-    ```javascript
-    () => {
-      const inputs = Array.from(
-        document.querySelectorAll('input, select, textarea'),
-      );
-      return inputs
+    ```js
+    () =>
+      Array.from(document.querySelectorAll('input, select, textarea'))
         .filter(i => {
           const hasId = i.id && document.querySelector(`label[for="${i.id}"]`);
           const hasAria =
             i.getAttribute('aria-label') || i.getAttribute('aria-labelledby');
-          const hasImplicitLabel = i.closest('label');
-          return !hasId && !hasAria && !hasImplicitLabel;
+          return !hasId && !hasAria && !i.closest('label');
         })
         .map(i => ({
           tag: i.tagName,
           id: i.id,
           name: i.name,
           placeholder: i.placeholder,
         }));
-    };
     ```
 
 ````
@@ -73,15 +68,15 @@ Testing "keyboard traps" and proper focus management without visual feedback rel
 
 According to web.dev, tap targets should be at least 48x48 pixels with sufficient spacing. Since the accessibility tree doesn't show sizes, use `evaluate_script`:
 
-```javascript
+```js
 // Usage in console: copy, paste, and call with element: fn(element)
 el => {
  const rect = el.getBoundingClientRect();
  return {width: rect.width, height: rect.height};
 };
 ````
 
-_Pass the element's `uid` from the snapshot as an argument to the tool._
+_Pass the element's `uid` from the snapshot as an argument to `evaluate_script`._
 
 ### 6. Color Contrast
 
@@ -94,7 +89,7 @@ If native audits do not report issues (which may happen in some headless environ
 
 **Note**: This script uses a simplified algorithm and may not account for transparency, gradients, or background images. For production-grade auditing, consider injecting `axe-core`.
 
-```javascript
+```js
 el => {
   function getRGB(colorStr) {
     const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
@@ -133,28 +128,19 @@ _Pass the element's `uid` to test the contrast against WCAG AA (4.5:1 for normal
 
 Verify document-level accessibility settings often missed in component testing:
 
-```javascript
-(() => {
-  const f = () => {
-    return {
-      lang:
-        document.documentElement.lang ||
-        'MISSING - Screen readers need this for pronunciation',
-      title: document.title || 'MISSING - Required for context',
-      viewport:
-        document.querySelector('meta[name="viewport"]')?.content ||
-        'MISSING - Check for user-scalable=no (bad practice)',
-      reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)')
-        .matches
-        ? 'Enabled'
-        : 'Disabled',
-    };
-  };
-  try {
-    console.log(f());
-  } catch (e) {} // Log for manual console usage
-  return f;
-})();
+```js
+() => ({
+  lang:
+    document.documentElement.lang ||
+    'MISSING - Screen readers need this for pronunciation',
+  title: document.title || 'MISSING - Required for context',
+  viewport:
+    document.querySelector('meta[name="viewport"]')?.content ||
+    'MISSING - Check for user-scalable=no (bad practice)',
+  reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
+    ? 'Enabled'
+    : 'Disabled',
+});
 ```
 
 ## Troubleshooting
PATCH

echo "Gold patch applied."
