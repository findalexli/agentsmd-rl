#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency check: if the fix is already applied, exit cleanly.
if grep -q "^  if (name === 'className') return { attr: 'class' }$" packages/component/src/lib/diff-props.ts; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/component/.changes/patch.fix-svg-classname-mapping.md b/packages/component/.changes/patch.fix-svg-classname-mapping.md
new file mode 100644
index 00000000000..9e567b3d98e
--- /dev/null
+++ b/packages/component/.changes/patch.fix-svg-classname-mapping.md
@@ -0,0 +1,3 @@
+Fix SVG `className` prop normalization to render as `class` in both client DOM updates and SSR stream output.
+
+Also add SVG regression coverage to prevent accidental `class-name` output.
diff --git a/packages/component/src/lib/diff-props.ts b/packages/component/src/lib/diff-props.ts
index 8cfacc1c34b..f6c95237dca 100644
--- a/packages/component/src/lib/diff-props.ts
+++ b/packages/component/src/lib/diff-props.ts
@@ -76,8 +76,8 @@ function normalizePropName(name: string, isSvg: boolean): { ns?: string; attr: s
   if (name.startsWith('aria-') || name.startsWith('data-')) return { attr: name }

   // DOM property -> HTML mappings
+  if (name === 'className') return { attr: 'class' }
   if (!isSvg) {
-    if (name === 'className') return { attr: 'class' }
     if (name === 'htmlFor') return { attr: 'for' }
     if (name === 'tabIndex') return { attr: 'tabindex' }
     if (name === 'acceptCharset') return { attr: 'accept-charset' }
diff --git a/packages/component/src/lib/stream.ts b/packages/component/src/lib/stream.ts
index d2151df3c3f..824b486ea70 100644
--- a/packages/component/src/lib/stream.ts
+++ b/packages/component/src/lib/stream.ts
@@ -794,8 +794,8 @@ function transformAttributeName(name: string, isSvg: boolean): string {
   if (name.startsWith('aria-') || name.startsWith('data-')) return name

   // HTML mappings
+  if (name === 'className') return 'class'
   if (!isSvg) {
-    if (name === 'className') return 'class'
     if (name === 'htmlFor') return 'for'
     if (name === 'tabIndex') return 'tabindex'
     if (name === 'acceptCharset') return 'accept-charset'
diff --git a/packages/component/src/test/stream.test.tsx b/packages/component/src/test/stream.test.tsx
index c3eb1e718b1..d9c47196f92 100644
--- a/packages/component/src/test/stream.test.tsx
+++ b/packages/component/src/test/stream.test.tsx
@@ -455,13 +455,13 @@ describe('stream', () => {
   describe('svg', () => {
     it('renders SVG with preserved viewBox and kebab-cased attributes', async () => {
       let stream = renderToStream(
-        <svg viewBox="0 0 24 24" fill="none">
+        <svg viewBox="0 0 24 24" fill="none" className="icon">
           <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
         </svg>,
       )
       let html = await drain(stream)
       expect(html).toBe(
-        '<svg viewBox="0 0 24 24" fill="none"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"></path></svg>',
+        '<svg viewBox="0 0 24 24" fill="none" class="icon"><path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5"></path></svg>',
       )
     })

diff --git a/packages/component/src/test/vdom.svg.test.tsx b/packages/component/src/test/vdom.svg.test.tsx
index add94d301ed..471e868902d 100644
--- a/packages/component/src/test/vdom.svg.test.tsx
+++ b/packages/component/src/test/vdom.svg.test.tsx
@@ -11,7 +11,7 @@ describe('vnode rendering', () => {
       let { render } = createRoot(container)

       render(
-        <svg viewBox="0 0 24 24" fill="none">
+        <svg viewBox="0 0 24 24" fill="none" class="icon">
           <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
         </svg>,
       )
@@ -26,6 +26,7 @@ describe('vnode rendering', () => {

       // Attribute casing: preserve exceptions and kebab-case general SVG attrs
       expect(svg.getAttribute('viewBox')).toBe('0 0 24 24')
+      expect(svg.getAttribute('class')).toBe('icon')
       expect(path.getAttribute('stroke-linecap')).toBe('round')
       expect(path.getAttribute('stroke-linejoin')).toBe('round')
     })
PATCH

echo "Patch applied successfully."
