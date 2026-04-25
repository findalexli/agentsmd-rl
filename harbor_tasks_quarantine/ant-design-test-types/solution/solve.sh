#!/bin/bash
set -e

cd /workspace/ant-design

# Check if already applied
if grep -q "type SnapshotTarget = HTMLElement" tests/setupAfterEnv.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/package.json b/package.json
index df5085b74b65..27a495b17862 100644
--- a/package.json
+++ b/package.json
@@ -327,6 +327,17 @@
   "publishConfig": {
     "registry": "https://registry.npmjs.org/"
   },
+  "pnpm": {
+    "overrides": {
+      "@sinonjs/fake-timers": "15.2.0"
+    }
+  },
+  "overrides": {
+    "@sinonjs/fake-timers": "15.2.0"
+  },
+  "resolutions": {
+    "@sinonjs/fake-timers": "15.2.0"
+  },
   "size-limit": [
     {
       "path": "./dist/antd.min.js",
diff --git a/tests/setupAfterEnv.ts b/tests/setupAfterEnv.ts
index 2a3ec7d0afac..7df9a35d3333 100644
--- a/tests/setupAfterEnv.ts
+++ b/tests/setupAfterEnv.ts
@@ -24,6 +24,8 @@ if (process.env.LIB_DIR === 'dist') {
   });
 }

+type SnapshotTarget = HTMLElement | DocumentFragment | HTMLCollection | NodeList | Node[];
+
 function cleanup(node: HTMLElement) {
   const childList = Array.from(node.childNodes);
   node.innerHTML = '';
@@ -37,12 +39,12 @@ function cleanup(node: HTMLElement) {
   return node;
 }

-function formatHTML(nodes: any) {
-  let cloneNodes: any;
+function formatHTML(nodes: SnapshotTarget) {
+  let cloneNodes: Node | Node[];
   if (Array.isArray(nodes) || nodes instanceof HTMLCollection || nodes instanceof NodeList) {
-    cloneNodes = Array.from(nodes).map((node) => cleanup(node.cloneNode(true) as any));
+    cloneNodes = Array.from(nodes).map((node) => cleanup(node.cloneNode(true) as HTMLElement));
   } else {
-    cloneNodes = cleanup(nodes.cloneNode(true));
+    cloneNodes = cleanup(nodes.cloneNode(true) as HTMLElement);
   }

   const htmlContent = format(cloneNodes, {
@@ -81,7 +83,7 @@ expect.addSnapshotSerializer({
       element instanceof DocumentFragment ||
       element instanceof HTMLCollection ||
       (Array.isArray(element) && element[0] instanceof HTMLElement)),
-  print: (element) => formatHTML(element),
+  print: (element) => formatHTML(element as SnapshotTarget),
 });

 /** Demo Test only accept render as SSR to make sure align with both `server` & `client` side */
@@ -106,7 +108,7 @@ expect.addSnapshotSerializer({
       }
     });

-    return formatHTML(children.length > 1 ? children : children[0]);
+    return formatHTML((children.length > 1 ? children : children[0]) as SnapshotTarget);
   },
 });

diff --git a/tests/shared/focusTest.tsx b/tests/shared/focusTest.tsx
index 1f2dab8ea9bc..7a1f86f97ee2 100644
--- a/tests/shared/focusTest.tsx
+++ b/tests/shared/focusTest.tsx
@@ -2,6 +2,11 @@ import React from 'react';

 import { fireEvent, render, sleep } from '../utils';

+type FocusableRef = {
+  focus: () => void;
+  blur: () => void;
+};
+
 const focusTest = (
   Component: React.ComponentType<any>,
   { refFocus = false, blurDelay = 0 } = {},
@@ -40,42 +45,47 @@ const focusTest = (
       document.body.removeChild(containerHtml);
     });

-    const getElement = (container: HTMLElement) =>
-      container.querySelector('input') ||
-      container.querySelector('button') ||
-      container.querySelector('textarea') ||
-      container.querySelector('div[tabIndex]');
+    const getElement = (container: HTMLElement): HTMLElement => {
+      const element =
+        container.querySelector<HTMLElement>('input') ||
+        container.querySelector<HTMLElement>('button') ||
+        container.querySelector<HTMLElement>('textarea') ||
+        container.querySelector<HTMLElement>('div[tabIndex]');
+
+      expect(element).not.toBeNull();
+      return element!;
+    };

     if (refFocus) {
       it('Ref: focus() and onFocus', () => {
         const onFocus = jest.fn();
-        const ref = React.createRef<any>();
+        const ref = React.createRef<FocusableRef>();
         const { container } = render(
           <div>
             <Component onFocus={onFocus} ref={ref} />
           </div>,
         );
-        ref.current.focus();
+        ref.current!.focus();
         expect(focused).toBeTruthy();

-        fireEvent.focus(getElement(container)!);
+        fireEvent.focus(getElement(container));
         expect(onFocus).toHaveBeenCalled();
       });

       it('Ref: blur() and onBlur', async () => {
         jest.useRealTimers();
         const onBlur = jest.fn();
-        const ref = React.createRef<any>();
+        const ref = React.createRef<FocusableRef>();
         const { container } = render(
           <div>
             <Component onBlur={onBlur} ref={ref} />
           </div>,
         );

-        ref.current.blur();
+        ref.current!.blur();
         expect(blurred).toBeTruthy();

-        fireEvent.blur(getElement(container)!);
+        fireEvent.blur(getElement(container));
         await sleep(blurDelay);
         expect(onBlur).toHaveBeenCalled();
       });
@@ -86,14 +96,14 @@ const focusTest = (

         expect(focused).toBeTruthy();

-        fireEvent.focus(getElement(container)!);
+        fireEvent.focus(getElement(container));
         expect(onFocus).toHaveBeenCalled();
       });
     } else {
       it('focus() and onFocus', () => {
         const handleFocus = jest.fn();
         const { container } = render(<Component onFocus={handleFocus} />);
-        fireEvent.focus(getElement(container)!);
+        fireEvent.focus(getElement(container));
         expect(handleFocus).toHaveBeenCalled();
       });

@@ -101,9 +111,9 @@ const focusTest = (
         jest.useRealTimers();
         const handleBlur = jest.fn();
         const { container } = render(<Component onBlur={handleBlur} />);
-        fireEvent.focus(getElement(container)!);
+        fireEvent.focus(getElement(container));
         await sleep(0);
-        fireEvent.blur(getElement(container)!);
+        fireEvent.blur(getElement(container));
         await sleep(0);
         expect(handleBlur).toHaveBeenCalled();
       });
PATCH

echo "Patch applied successfully"
