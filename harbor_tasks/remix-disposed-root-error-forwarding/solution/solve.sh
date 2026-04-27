#!/usr/bin/env bash
# Oracle solution: applies the gold patch from PR #11113 inline (no network fetch).
set -euo pipefail

cd /workspace/remix

# Idempotency guard — bail if the patch is already applied.
if grep -q 'function detachDomErrorForwarding' packages/component/src/lib/vdom.ts 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/component/src/lib/vdom.ts b/packages/component/src/lib/vdom.ts
index ec603199a2a..1beac15623b 100644
--- a/packages/component/src/lib/vdom.ts
+++ b/packages/component/src/lib/vdom.ts
@@ -53,12 +53,13 @@ export function createRangeRoot(
   let container = end.parentNode
   invariant(container, 'Expected parent node')
   invariant(start.parentNode === container, 'Boundaries must share parent')
+  let parent = container

   let hydrationCursor = start.nextSibling

   let eventTarget = new TypedEventTarget<VirtualRootEventMap>()
   let scheduler =
-    options.scheduler ?? createScheduler(container.ownerDocument ?? document, eventTarget, styles)
+    options.scheduler ?? createScheduler(parent.ownerDocument ?? document, eventTarget, styles)
   let frameStub =
     options.frame ??
     createRootFrameHandle({
@@ -69,13 +70,26 @@ export function createRangeRoot(
       styleManager: styles,
     })

-  // Forward bubbling error events from DOM to root EventTarget
-  container.addEventListener('error', (event) => {
+  let isErrorForwardingAttached = false
+  function forwardDomError(event: Event) {
     eventTarget.dispatchEvent(new ErrorEvent('error', { error: (event as ErrorEvent).error }))
-  })
+  }
+  function attachDomErrorForwarding() {
+    if (isErrorForwardingAttached) return
+    parent.addEventListener('error', forwardDomError)
+    isErrorForwardingAttached = true
+  }
+  function detachDomErrorForwarding() {
+    if (!isErrorForwardingAttached) return
+    parent.removeEventListener('error', forwardDomError)
+    isErrorForwardingAttached = false
+  }
+  attachDomErrorForwarding()

   return Object.assign(eventTarget, {
     render(element: RemixNode) {
+      attachDomErrorForwarding()
+
       let vnode = toVNode(element)
       let vParent: VNode = {
         type: ROOT_VNODE,
@@ -89,7 +103,7 @@ export function createRangeRoot(
           diffVNodes(
             vroot,
             vnode,
-            container,
+            parent,
             frameStub,
             scheduler,
             styles,
@@ -106,10 +120,12 @@ export function createRangeRoot(
     },

     dispose() {
+      detachDomErrorForwarding()
+
       if (!vroot) return
       let current = vroot
       vroot = null
-      scheduler.enqueueTasks([() => removeVNode(current, container, scheduler, styles)])
+      scheduler.enqueueTasks([() => removeVNode(current, parent, scheduler, styles)])
       scheduler.dequeue()
     },

@@ -137,13 +153,26 @@ export function createRoot(container: HTMLElement, options: VirtualRootOptions =
       styleManager: styles,
     })

-  // Forward bubbling error events from DOM to root EventTarget
-  container.addEventListener('error', (event) => {
+  let isErrorForwardingAttached = false
+  function forwardDomError(event: Event) {
     eventTarget.dispatchEvent(new ErrorEvent('error', { error: (event as ErrorEvent).error }))
-  })
+  }
+  function attachDomErrorForwarding() {
+    if (isErrorForwardingAttached) return
+    container.addEventListener('error', forwardDomError)
+    isErrorForwardingAttached = true
+  }
+  function detachDomErrorForwarding() {
+    if (!isErrorForwardingAttached) return
+    container.removeEventListener('error', forwardDomError)
+    isErrorForwardingAttached = false
+  }
+  attachDomErrorForwarding()

   return Object.assign(eventTarget, {
     render(element: RemixNode) {
+      attachDomErrorForwarding()
+
       let vnode = toVNode(element)
       let vParent: VNode = { type: ROOT_VNODE, _svg: false }
       scheduler.enqueueTasks([
@@ -168,6 +197,8 @@ export function createRoot(container: HTMLElement, options: VirtualRootOptions =
     },

     dispose() {
+      detachDomErrorForwarding()
+
       if (!vroot) return
       let current = vroot
       vroot = null
PATCH

echo "Gold patch applied."
