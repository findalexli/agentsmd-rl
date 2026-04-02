#!/bin/bash
set -euo pipefail

# Solution script: Stabilize reactFragments host node handle
# PR: facebook/react#35642

# Check if already applied (grep for stabilized property name)
if grep -q "reactFragments?: Set<FragmentInstanceType>" packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
index fc1039faaa0c..4cb4e8e4273a 100644
--- a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
+++ b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
@@ -218,7 +218,7 @@ export type Instance = Element;
 export type TextInstance = Text;

 type InstanceWithFragmentHandles = Instance & {
-  unstable_reactFragments?: Set<FragmentInstanceType>,
+  reactFragments?: Set<FragmentInstanceType>,
 };

 declare class ActivityInterface extends Comment {}
@@ -3578,10 +3578,10 @@ function addFragmentHandleToInstance(
   fragmentInstance: FragmentInstanceType,
 ): void {
   if (enableFragmentRefsInstanceHandles) {
-    if (instance.unstable_reactFragments == null) {
-      instance.unstable_reactFragments = new Set();
+    if (instance.reactFragments == null) {
+      instance.reactFragments = new Set();
     }
-    instance.unstable_reactFragments.add(fragmentInstance);
+    instance.reactFragments.add(fragmentInstance);
   }
 }

@@ -3647,8 +3647,8 @@ export function deleteChildFromFragmentInstance(
     }
   }
   if (enableFragmentRefsInstanceHandles) {
-    if (instance.unstable_reactFragments != null) {
-      instance.unstable_reactFragments.delete(fragmentInstance);
+    if (instance.reactFragments != null) {
+      instance.reactFragments.delete(fragmentInstance);
     }
   }
 }
diff --git a/packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js b/packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js
index 603af9072b6e..aed4f5252f84 100644
--- a/packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js
+++ b/packages/react-dom/src/__tests__/ReactDOMFragmentRefs-test.js
@@ -137,26 +137,18 @@ describe('FragmentRefs', () => {
     const childB = document.querySelector('#childB');
     const childC = document.querySelector('#childC');

-    expect(childA.unstable_reactFragments.has(fragmentRef.current)).toBe(true);
-    expect(childB.unstable_reactFragments.has(fragmentRef.current)).toBe(true);
-    expect(childC.unstable_reactFragments.has(fragmentRef.current)).toBe(false);
-    expect(childA.unstable_reactFragments.has(fragmentParentRef.current)).toBe(
-      true,
-    );
-    expect(childB.unstable_reactFragments.has(fragmentParentRef.current)).toBe(
-      true,
-    );
-    expect(childC.unstable_reactFragments.has(fragmentParentRef.current)).toBe(
-      true,
-    );
+    expect(childA.reactFragments.has(fragmentRef.current)).toBe(true);
+    expect(childB.reactFragments.has(fragmentRef.current)).toBe(true);
+    expect(childC.reactFragments.has(fragmentRef.current)).toBe(false);
+    expect(childA.reactFragments.has(fragmentParentRef.current)).toBe(true);
+    expect(childB.reactFragments.has(fragmentParentRef.current)).toBe(true);
+    expect(childC.reactFragments.has(fragmentParentRef.current)).toBe(true);

     await act(() => root.render(<Test show={true} />));

     const childD = document.querySelector('#childD');
-    expect(childD.unstable_reactFragments.has(fragmentRef.current)).toBe(false);
-    expect(childD.unstable_reactFragments.has(fragmentParentRef.current)).toBe(
-      true,
-    );
+    expect(childD.reactFragments.has(fragmentRef.current)).toBe(false);
+    expect(childD.reactFragments.has(fragmentParentRef.current)).toBe(true);
   });

   describe('focus methods', () => {
@@ -1104,7 +1096,7 @@ describe('FragmentRefs', () =>
         }
         const observer = new IntersectionObserver(entries => {
           entries.forEach(entry => {
-            const fragmentInstances = entry.target.unstable_reactFragments;
+            const fragmentInstances = entry.target.reactFragments;
             if (fragmentInstances) {
               Array.from(fragmentInstances).forEach(fInstance => {
                 const cbs = targetToCallbackMap.get(fInstance) || [];
diff --git a/packages/react-native-renderer/src/ReactFiberConfigFabric.js b/packages/react-native-renderer/src/ReactFiberConfigFabric.js
index 26f921bf4297..18c4eaddd9ea 100644
--- a/packages/react-native-renderer/src/ReactFiberConfigFabric.js
+++ b/packages/react-native-renderer/src/ReactFiberConfigFabric.js
@@ -124,7 +124,7 @@ export type TextInstance = {
 export type HydratableInstance = Instance | TextInstance;
 export type PublicInstance = ReactNativePublicInstance;
 type PublicInstanceWithFragmentHandles = PublicInstance & {
-  unstable_reactFragments?: Set<FragmentInstanceType>,
+  reactFragments?: Set<FragmentInstanceType>,
 };
 export type Container = {
   containerTag: number,
@@ -856,10 +856,10 @@ function addFragmentHandleToInstance(
   fragmentInstance: FragmentInstanceType,
 ): void {
   if (enableFragmentRefsInstanceHandles) {
-    if (instance.unstable_reactFragments == null) {
-      instance.unstable_reactFragments = new Set();
+    if (instance.reactFragments == null) {
+      instance.reactFragments = new Set();
     }
-    instance.unstable_reactFragments.add(fragmentInstance);
+    instance.reactFragments.add(fragmentInstance);
   }
 }

@@ -924,8 +924,8 @@ export function deleteChildFromFragmentInstance(
     instance,
   ): any): PublicInstanceWithFragmentHandles);
   if (enableFragmentRefsInstanceHandles) {
-    if (publicInstance.unstable_reactFragments != null) {
-      publicInstance.unstable_reactFragments.delete(fragmentInstance);
+    if (publicInstance.reactFragments != null) {
+      publicInstance.reactFragments.delete(fragmentInstance);
     }
   }
 }
PATCH

echo "Patch applied successfully"
