#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency guard: skip if already applied
if grep -q "clearRuntimePropertyOnRemoval" packages/component/src/lib/diff-props.ts 2>/dev/null; then
  echo "Patch already applied, skipping."
  exit 0
fi

git apply <<'PATCH'
diff --git a/packages/component/.changes/patch.fix-prop-removal-attribute-cleanup.md b/packages/component/.changes/patch.fix-prop-removal-attribute-cleanup.md
new file mode 100644
index 00000000000..edf01331c08
--- /dev/null
+++ b/packages/component/.changes/patch.fix-prop-removal-attribute-cleanup.md
@@ -0,0 +1,3 @@
+Fix host prop removal to fully remove reflected attributes while still resetting runtime form control state.
+
+Adds regression coverage for attribute removal/update behavior to prevent empty-attribute regressions.
diff --git a/packages/component/src/lib/diff-props.ts b/packages/component/src/lib/diff-props.ts
index 3307b790d2f..1d03154df0a 100644
--- a/packages/component/src/lib/diff-props.ts
+++ b/packages/component/src/lib/diff-props.ts
@@ -147,6 +147,25 @@ function camelToKebab(input: string): string {
     .toLowerCase()
 }

+function clearRuntimePropertyOnRemoval(
+  dom: Element & Record<string, unknown>,
+  name: string,
+): void {
+  try {
+    if (name === 'value' || name === 'defaultValue') {
+      dom[name] = ''
+      return
+    }
+    if (name === 'checked' || name === 'defaultChecked' || name === 'selected') {
+      dom[name] = false
+      return
+    }
+    if (name === 'selectedIndex') {
+      dom[name] = -1
+    }
+  } catch {}
+}
+
 export function diffHostProps(curr: ElementProps, next: ElementProps, dom: Element) {
   let isSvg = dom.namespaceURI === SVG_NS

@@ -158,12 +177,9 @@ export function diffHostProps(curr: ElementProps, next: ElementProps, dom: Eleme
   for (let name in curr) {
     if (isFrameworkProp(name)) continue
     if (!(name in next) || next[name] == null) {
-      // Prefer property clearing when applicable (align with Preact)
+      // Clear runtime state for form-like props where removing the attribute is not enough.
       if (canUseProperty(dom, name, isSvg)) {
-        try {
-          dom[name] = ''
-          continue
-        } catch {}
+        clearRuntimePropertyOnRemoval(dom, name)
       }

       let { ns, attr } = normalizePropName(name, isSvg)
diff --git a/packages/component/src/test/vdom.insert-remove.test.tsx b/packages/component/src/test/vdom.insert-remove.test.tsx
index a11c4ef3f52..763299feb34 100644
--- a/packages/component/src/test/vdom.insert-remove.test.tsx
+++ b/packages/component/src/test/vdom.insert-remove.test.tsx
@@ -83,18 +83,40 @@ describe('vnode rendering', () => {
       expect(container.innerHTML).toBe('<div></div>')
     })

-    it.skip('removes attributes', () => {
+    it('removes attributes', () => {
       let container = document.createElement('div')
       let root = createRoot(container)
       root.render(<input id="hello" value="world" />)
       let input = container.querySelector('input')
       expect(input).toBeInstanceOf(HTMLInputElement)
       expect((input as HTMLInputElement).value).toBe('world')
-      expect(container.innerHTML).toBe('<input id="hello">')
+      expect((input as HTMLInputElement).getAttribute('id')).toBe('hello')
       root.render(<input />)
       root.flush()
       expect((input as HTMLInputElement).value).toBe('')
-      expect(container.innerHTML).toBe('<input id="">') // FIXME: should be <input>
+      expect((input as HTMLInputElement).hasAttribute('id')).toBe(false)
+      expect((input as HTMLInputElement).hasAttribute('value')).toBe(false)
+    })
+
+    it('removes reflected attributes without leaving empty values', () => {
+      let container = document.createElement('div')
+      let root = createRoot(container)
+      root.render(
+        <div id="hello" className="world">
+          content
+        </div>,
+      )
+
+      let div = container.querySelector('div')
+      expect(div).toBeInstanceOf(HTMLDivElement)
+      expect((div as HTMLDivElement).getAttribute('id')).toBe('hello')
+      expect((div as HTMLDivElement).getAttribute('class')).toBe('world')
+
+      root.render(<div>content</div>)
+      root.flush()
+
+      expect((div as HTMLDivElement).hasAttribute('id')).toBe(false)
+      expect((div as HTMLDivElement).hasAttribute('class')).toBe(false)
     })

     it('removes a fragment', () => {
diff --git a/packages/component/src/test/vdom.replacements.test.tsx b/packages/component/src/test/vdom.replacements.test.tsx
index 95049933818..ebffb18353a 100644
--- a/packages/component/src/test/vdom.replacements.test.tsx
+++ b/packages/component/src/test/vdom.replacements.test.tsx
@@ -26,16 +26,19 @@ describe('vnode rendering', () => {
       expect(container.querySelector('div')).toBe(div)
     })

-    it.skip('updates an element with attributes', () => {
+    it('updates an element with attributes', () => {
       let container = document.createElement('div')
       let { render } = createRoot(container)
       render(<input id="hello" value="world" />)
-      expect(container.innerHTML).toBe('<input id="hello" value="world">')
-
       let input = container.querySelector('input')
+      invariant(input)
+      expect(input.getAttribute('id')).toBe('hello')
+      expect(input.value).toBe('world')
+
       render(<input id="hello" value="world 2" />)
-      expect(container.innerHTML).toBe('<input id="hello" value="world 2">')
       expect(container.querySelector('input')).toBe(input)
+      expect(input.getAttribute('id')).toBe('hello')
+      expect(input.value).toBe('world 2')
     })

     it('updates a fragment', () => {
PATCH
