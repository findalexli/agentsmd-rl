#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'suspendedSetByRendererID' packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/__tests__/store-test.js b/packages/react-devtools-shared/src/__tests__/store-test.js
index 36198ac1e079..2e56462aac9a 100644
--- a/packages/react-devtools-shared/src/__tests__/store-test.js
+++ b/packages/react-devtools-shared/src/__tests__/store-test.js
@@ -981,6 +981,7 @@ describe('Store', () => {

       await actAsync(() => {
         agent.overrideSuspenseMilestone({
+          rendererID: getRendererID(),
           suspendedSet: [
             store.getElementIDAtIndex(4),
             store.getElementIDAtIndex(8),
@@ -1010,6 +1011,7 @@ describe('Store', () => {

       await actAsync(() => {
         agent.overrideSuspenseMilestone({
+          rendererID: getRendererID(),
           suspendedSet: [],
         });
       });
diff --git a/packages/react-devtools-shared/src/backend/agent.js b/packages/react-devtools-shared/src/backend/agent.js
index 78387326f379..18f3e208408b 100644
--- a/packages/react-devtools-shared/src/backend/agent.js
+++ b/packages/react-devtools-shared/src/backend/agent.js
@@ -147,6 +147,7 @@ type OverrideSuspenseParams = {
 };

 type OverrideSuspenseMilestoneParams = {
+  rendererID: number,
   suspendedSet: Array<number>,
 };

@@ -787,15 +788,14 @@ export default class Agent extends EventEmitter<{
   };

   overrideSuspenseMilestone: OverrideSuspenseMilestoneParams => void = ({
+    rendererID,
     suspendedSet,
   }) => {
-    for (const rendererID in this._rendererInterfaces) {
-      const renderer = ((this._rendererInterfaces[
-        (rendererID: any)
-      ]: any): RendererInterface);
-      if (renderer.supportsTogglingSuspense) {
-        renderer.overrideSuspenseMilestone(suspendedSet);
-      }
+    const renderer = ((this._rendererInterfaces[
+      (rendererID: any)
+    ]: any): RendererInterface);
+    if (renderer.supportsTogglingSuspense) {
+      renderer.overrideSuspenseMilestone(suspendedSet);
     }
   };

diff --git a/packages/react-devtools-shared/src/bridge.js b/packages/react-devtools-shared/src/bridge.js
index 2e30e909841f..ba4b2a0f8061 100644
--- a/packages/react-devtools-shared/src/bridge.js
+++ b/packages/react-devtools-shared/src/bridge.js
@@ -145,6 +145,7 @@ type OverrideSuspense = {
 };

 type OverrideSuspenseMilestone = {
+  rendererID: number,
   suspendedSet: Array<number>,
 };

diff --git a/packages/react-devtools-shared/src/devtools/store.js b/packages/react-devtools-shared/src/devtools/store.js
index 5466e798aad4..3849da9e5736 100644
--- a/packages/react-devtools-shared/src/devtools/store.js
+++ b/packages/react-devtools-shared/src/devtools/store.js
@@ -957,6 +957,12 @@ export default class Store extends EventEmitter<{
       if (root === null) {
         continue;
       }
+      const rendererID = this._rootIDToRendererID.get(rootID);
+      if (rendererID === undefined) {
+        throw new Error(
+          'Failed to find renderer ID for root. This is a bug in React DevTools.',
+        );
+      }
       // TODO: This includes boundaries that can't be suspended due to no support from the renderer.

       const suspense = this.getSuspenseByID(rootID);
@@ -972,6 +978,7 @@ export default class Store extends EventEmitter<{
             id: suspense.id,
             environment: environmentName,
             endTime: suspense.endTime,
+            rendererID,
           };
           target.push(rootStep);
         } else {
@@ -990,6 +997,7 @@ export default class Store extends EventEmitter<{
           uniqueSuspendersOnly,
           environments,
           0, // Don't pass a minimum end time at the root. The root is always first so doesn't matter.
+          rendererID,
         );
       }
     }
@@ -1039,6 +1047,7 @@ export default class Store extends EventEmitter<{
    */
   getSuspendableDocumentOrderSuspenseTransition(
     uniqueSuspendersOnly: boolean,
+    rendererID: number,
   ): Array<SuspenseTimelineStep> {
     const target: Array<SuspenseTimelineStep> = [];
     const focusedTransitionID = this._focusedTransition;
@@ -1051,6 +1060,7 @@ export default class Store extends EventEmitter<{
       // TODO: Get environment for Activity
       environment: null,
       endTime: 0,
+      rendererID,
     });

     const transitionChildren = this.getSuspenseChildren(focusedTransitionID);
@@ -1062,6 +1072,7 @@ export default class Store extends EventEmitter<{
       // TODO: Get environment for Activity
       [],
       0, // Don't pass a minimum end time at the root. The root is always first so doesn't matter.
+      rendererID,
     );

     return target;
@@ -1073,6 +1084,7 @@ export default class Store extends EventEmitter<{
     uniqueSuspendersOnly: boolean,
     parentEnvironments: Array<string>,
     parentEndTime: number,
+    rendererID: number,
   ): void {
     for (let i = 0; i < children.length; i++) {
       const child = this.getSuspenseByID(children[i]);
@@ -1106,6 +1118,7 @@ export default class Store extends EventEmitter<{
           id: child.id,
           environment: environmentName,
           endTime: maxEndTime,
+          rendererID,
         });
       }
       this.pushTimelineStepsInDocumentOrder(
@@ -1114,6 +1127,7 @@ export default class Store extends EventEmitter<{
         uniqueSuspendersOnly,
         unionEnvironments,
         maxEndTime,
+        rendererID,
       );
     }
   }
@@ -1121,14 +1135,32 @@ export default class Store extends EventEmitter<{
   getEndTimeOrDocumentOrderSuspense(
     uniqueSuspendersOnly: boolean,
   ): $ReadOnlyArray<SuspenseTimelineStep> {
-    const timeline =
-      this._focusedTransition === 0
-        ? this.getSuspendableDocumentOrderSuspenseInitialPaint(
-            uniqueSuspendersOnly,
-          )
-        : this.getSuspendableDocumentOrderSuspenseTransition(
-            uniqueSuspendersOnly,
-          );
+    let timeline: SuspenseTimelineStep[];
+    if (this._focusedTransition === 0) {
+      timeline =
+        this.getSuspendableDocumentOrderSuspenseInitialPaint(
+          uniqueSuspendersOnly,
+        );
+    } else {
+      const focusedTransitionRootID = this.getRootIDForElement(
+        this._focusedTransition,
+      );
+      if (focusedTransitionRootID === null) {
+        throw new Error(
+          'Failed to find root ID for focused transition. This is a bug in React DevTools.',
+        );
+      }
+      const rendererID = this._rootIDToRendererID.get(focusedTransitionRootID);
+      if (rendererID === undefined) {
+        throw new Error(
+          'Failed to find renderer ID for focused transition root. This is a bug in React DevTools.',
+        );
+      }
+      timeline = this.getSuspendableDocumentOrderSuspenseTransition(
+        uniqueSuspendersOnly,
+        rendererID,
+      );
+    }

     if (timeline.length === 0) {
       return timeline;
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js
index 89f349ae6ea7..c7d9246fb457 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTimeline.js
@@ -9,7 +9,7 @@

 import * as React from 'react';
 import {useContext, useEffect} from 'react';
-import {BridgeContext} from '../context';
+import {BridgeContext, StoreContext} from '../context';
 import {TreeDispatcherContext} from '../Components/TreeContext';
 import {useScrollToHostInstance} from '../hooks';
 import {
@@ -20,9 +20,11 @@ import styles from './SuspenseTimeline.css';
 import SuspenseScrubber from './SuspenseScrubber';
 import Button from '../Button';
 import ButtonIcon from '../ButtonIcon';
+import type {SuspenseNode} from '../../../frontend/types';

 function SuspenseTimelineInput() {
   const bridge = useContext(BridgeContext);
+  const store = useContext(StoreContext);
   const treeDispatch = useContext(TreeDispatcherContext);
   const suspenseTreeDispatch = useContext(SuspenseTreeDispatcherContext);
   const scrollToHostInstance = useScrollToHostInstance();
@@ -101,15 +103,43 @@ function SuspenseTimelineInput() {
   // TODO: useEffectEvent here once it's supported in all versions DevTools supports.
   // For now we just exclude it from deps since we don't lint those anyway.
   function changeTimelineIndex(newIndex: number) {
+    const suspendedSetByRendererID = new Map<
+      number,
+      Array<SuspenseNode['id']>,
+    >();
+    // Unsuspend everything by default.
+    // We might not encounter every renderer after the milestone e.g.
+    // if we clicked at the end of the timeline.
+    // eslint-disable-next-line no-for-of-loops/no-for-of-loops
+    for (const rendererID of store.rootIDToRendererID.values()) {
+      suspendedSetByRendererID.set(rendererID, []);
+    }
+
     // Synchronize timeline index with what is resuspended.
     // We suspend everything after the current selection. The root isn't showing
     // anything suspended in the root. The step after that should have one less
     // thing suspended. I.e. the first suspense boundary should be unsuspended
     // when it's selected. This also lets you show everything in the last step.
-    const suspendedSet = timeline.slice(timelineIndex + 1).map(step => step.id);
-    bridge.send('overrideSuspenseMilestone', {
-      suspendedSet,
-    });
+    for (let i = timelineIndex + 1; i < timeline.length; i++) {
+      const step = timeline[i];
+      const {rendererID} = step;
+      const suspendedSetForRendererID =
+        suspendedSetByRendererID.get(rendererID);
+      if (suspendedSetForRendererID === undefined) {
+        throw new Error(
+          `Should have initialized suspended set for renderer ID "${rendererID}" earlier. This is a bug in React DevTools.`,
+        );
+      }
+      suspendedSetForRendererID.push(step.id);
+    }
+
+    // eslint-disable-next-line no-for-of-loops/no-for-of-loops
+    for (const [rendererID, suspendedSet] of suspendedSetByRendererID) {
+      bridge.send('overrideSuspenseMilestone', {
+        rendererID,
+        suspendedSet,
+      });
+    }
   }

   useEffect(() => {
diff --git a/packages/react-devtools-shared/src/frontend/types.js b/packages/react-devtools-shared/src/frontend/types.js
index a78831cf229b..98acc3ed43cc 100644
--- a/packages/react-devtools-shared/src/frontend/types.js
+++ b/packages/react-devtools-shared/src/frontend/types.js
@@ -210,6 +210,7 @@ export type SuspenseTimelineStep = {
    */
   id: SuspenseNode['id'] | Element['id'], // TODO: Will become a group.
   environment: null | string,
+  rendererID: number,
   endTime: number,
 };

PATCH

echo "Patch applied successfully."
