#!/bin/bash
set -euo pipefail

# This patch refactors FragmentInstance methods for better performance and correctness:
# 1. Early return in indexOfEventListener when array is empty
# 2. Early exit in blur() when activeElement is not within fragment's parent
# 3. Pass activeElement to traversal callback to avoid redundant lookups
# 4. Handle text nodes in blurActiveElementWithinFragment
# 5. Rename variables for clarity (element -> node)

FILE="packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"

# Check if already applied (grep for distinctive line from the patch)
if grep -q "Early exit if activeElement is not within the fragment's parent" "$FILE" 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

cd /workspace/react

git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
index 09653552aafe..c90d2a116c47 100644
--- a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
+++ b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
@@ -3056,13 +3056,16 @@ function indexOfEventListener(
   listener: EventListener,
   optionsOrUseCapture: void | EventListenerOptionsOrUseCapture,
 ): number {
+  if (eventListeners.length === 0) {
+    return -1;
+  }
+  const normalizedOptions = normalizeListenerOptions(optionsOrUseCapture);
   for (let i = 0; i < eventListeners.length; i++) {
     const item = eventListeners[i];
     if (
       item.type === type &&
       item.listener === listener &&
-      normalizeListenerOptions(item.optionsOrUseCapture) ===
-        normalizeListenerOptions(optionsOrUseCapture)
+      normalizeListenerOptions(item.optionsOrUseCapture) === normalizedOptions
     ) {
       return i;
     }
@@ -3154,18 +3157,34 @@ function collectChildren(child: Fiber, collection: Array<Fiber>): boolean {
 }
 // $FlowFixMe[prop-missing]
 FragmentInstance.prototype.blur = function (this: FragmentInstanceType): void {
-  // TODO: When we have a parent element reference, we can skip traversal if the fragment's parent
-  //   does not contain document.activeElement
+  // Early exit if activeElement is not within the fragment's parent
+  const parentHostFiber = getFragmentParentHostFiber(this._fragmentFiber);
+  if (parentHostFiber === null) {
+    return;
+  }
+  const parentHostInstance =
+    getInstanceFromHostFiber<Instance>(parentHostFiber);
+  const activeElement = parentHostInstance.ownerDocument.activeElement;
+  if (activeElement === null || !parentHostInstance.contains(activeElement)) {
+    return;
+  }
+
   traverseFragmentInstance(
     this._fragmentFiber,
     blurActiveElementWithinFragment,
+    activeElement,
   );
 };
-function blurActiveElementWithinFragment(child: Fiber): boolean {
-  // TODO: We can get the activeElement from the parent outside of the loop when we have a reference.
+function blurActiveElementWithinFragment(
+  child: Fiber,
+  activeElement: Element,
+): boolean {
+  // Skip text nodes - they can't be focused
+  if (enableFragmentRefsTextNodes && child.tag === HostText) {
+    return false;
+  }
   const instance = getInstanceFromHostFiber<Instance>(child);
-  const ownerDocument = instance.ownerDocument;
-  if (instance === ownerDocument.activeElement) {
+  if (instance === activeElement) {
     // $FlowFixMe[prop-missing]
     instance.blur();
     return true;
@@ -3312,46 +3331,45 @@ FragmentInstance.prototype.compareDocumentPosition = function (
     );
   }

-  const firstElement = getInstanceFromHostFiber<Instance>(children[0]);
-  const lastElement = getInstanceFromHostFiber<Instance>(
+  const firstNode = getInstanceFromHostFiber<Instance>(children[0]);
+  const lastNode = getInstanceFromHostFiber<Instance>(
     children[children.length - 1],
   );

   // If the fragment has been portaled into another host instance, we need to
   // our best guess is to use the parent of the child instance, rather than
   // the fiber tree host parent.
-  const firstInstance = getInstanceFromHostFiber<Instance>(children[0]);
   const parentHostInstanceFromDOM = fiberIsPortaledIntoHost(this._fragmentFiber)
-    ? (firstInstance.parentElement: ?Instance)
+    ? (firstNode.parentElement: ?Instance)
     : parentHostInstance;

   if (parentHostInstanceFromDOM == null) {
     return Node.DOCUMENT_POSITION_DISCONNECTED;
   }

-  // Check if first and last element are actually in the expected document position
-  // before relying on them as source of truth for other contained elements
-  const firstElementIsContained =
-    parentHostInstanceFromDOM.compareDocumentPosition(firstElement) &
+  // Check if first and last node are actually in the expected document position
+  // before relying on them as source of truth for other contained nodes
+  const firstNodeIsContained =
+    parentHostInstanceFromDOM.compareDocumentPosition(firstNode) &
     Node.DOCUMENT_POSITION_CONTAINED_BY;
-  const lastElementIsContained =
-    parentHostInstanceFromDOM.compareDocumentPosition(lastElement) &
+  const lastNodeIsContained =
+    parentHostInstanceFromDOM.compareDocumentPosition(lastNode) &
     Node.DOCUMENT_POSITION_CONTAINED_BY;
-  const firstResult = firstElement.compareDocumentPosition(otherNode);
-  const lastResult = lastElement.compareDocumentPosition(otherNode);
+  const firstResult = firstNode.compareDocumentPosition(otherNode);
+  const lastResult = lastNode.compareDocumentPosition(otherNode);

   const otherNodeIsFirstOrLastChild =
-    (firstElementIsContained && firstElement === otherNode) ||
-    (lastElementIsContained && lastElement === otherNode);
+    (firstNodeIsContained && firstNode === otherNode) ||
+    (lastNodeIsContained && lastNode === otherNode);
   const otherNodeIsFirstOrLastChildDisconnected =
-    (!firstElementIsContained && firstElement === otherNode) ||
-    (!lastElementIsContained && lastElement === otherNode);
+    (!firstNodeIsContained && firstNode === otherNode) ||
+    (!lastNodeIsContained && lastNode === otherNode);
   const otherNodeIsWithinFirstOrLastChild =
     firstResult & Node.DOCUMENT_POSITION_CONTAINED_BY ||
     lastResult & Node.DOCUMENT_POSITION_CONTAINED_BY;
   const otherNodeIsBetweenFirstAndLastChildren =
-    firstElementIsContained &&
-    lastElementIsContained &&
+    firstNodeIsContained &&
+    lastNodeIsContained &&
     firstResult & Node.DOCUMENT_POSITION_FOLLOWING &&
     lastResult & Node.DOCUMENT_POSITION_PRECEDING;
PATCH

echo "Patch applied successfully"
