#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'flushingInShell' packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js b/packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js
index a93c32a947f1..e654ea88007d 100644
--- a/packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js
+++ b/packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js
@@ -7041,7 +7041,17 @@ export function hoistHoistables(
   }
 }

-export function hasSuspenseyContent(hoistableState: HoistableState): boolean {
+export function hasSuspenseyContent(
+  hoistableState: HoistableState,
+  flushingInShell: boolean,
+): boolean {
+  if (flushingInShell) {
+    // When flushing the shell, stylesheets with precedence are already emitted
+    // in the <head> which blocks paint. There's no benefit to outlining for CSS
+    // alone during the shell flush. However, suspensey images (for ViewTransition
+    // animation reveals) should still trigger outlining even during the shell.
+    return hoistableState.suspenseyImages;
+  }
   return hoistableState.stylesheets.size > 0 || hoistableState.suspenseyImages;
 }

diff --git a/packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js b/packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js
index d48e9a8dd932..46fad3c39bf4 100644
--- a/packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js
+++ b/packages/react-dom-bindings/src/server/ReactFizzConfigDOMLegacy.js
@@ -326,7 +326,10 @@ export function writePreambleStart(
   );
 }

-export function hasSuspenseyContent(hoistableState: HoistableState): boolean {
+export function hasSuspenseyContent(
+  hoistableState: HoistableState,
+  flushingInShell: boolean,
+): boolean {
   // Never outline.
   return false;
 }
diff --git a/packages/react-markup/src/ReactFizzConfigMarkup.js b/packages/react-markup/src/ReactFizzConfigMarkup.js
index 7dbe5592f337..d12d72e69e02 100644
--- a/packages/react-markup/src/ReactFizzConfigMarkup.js
+++ b/packages/react-markup/src/ReactFizzConfigMarkup.js
@@ -242,7 +242,10 @@ export function writeCompletedRoot(
   return true;
 }

-export function hasSuspenseyContent(hoistableState: HoistableState): boolean {
+export function hasSuspenseyContent(
+  hoistableState: HoistableState,
+  flushingInShell: boolean,
+): boolean {
   // Never outline.
   return false;
 }
diff --git a/packages/react-noop-renderer/src/ReactNoopServer.js b/packages/react-noop-renderer/src/ReactNoopServer.js
index 1793180cc765..913e72d7fc4f 100644
--- a/packages/react-noop-renderer/src/ReactNoopServer.js
+++ b/packages/react-noop-renderer/src/ReactNoopServer.js
@@ -324,7 +324,10 @@ const ReactNoopServer = ReactFizzServer({
   writeHoistablesForBoundary() {},
   writePostamble() {},
   hoistHoistables(parent: HoistableState, child: HoistableState) {},
-  hasSuspenseyContent(hoistableState: HoistableState): boolean {
+  hasSuspenseyContent(
+    hoistableState: HoistableState,
+    flushingInShell: boolean,
+  ): boolean {
     return false;
   },
   createHoistableState(): HoistableState {
diff --git a/packages/react-server/src/ReactFizzServer.js b/packages/react-server/src/ReactFizzServer.js
index d06d967b1f87..989f9184637d 100644
--- a/packages/react-server/src/ReactFizzServer.js
+++ b/packages/react-server/src/ReactFizzServer.js
@@ -479,7 +479,7 @@ function isEligibleForOutlining(
   // outlining.
   return (
     (boundary.byteSize > 500 ||
-      hasSuspenseyContent(boundary.contentState) ||
+      hasSuspenseyContent(boundary.contentState, /* flushingInShell */ false) ||
       boundary.defer) &&
     // For boundaries that can possibly contribute to the preamble we don't want to outline
     // them regardless of their size since the fallbacks should only be emitted if we've
@@ -5593,7 +5593,7 @@ function flushSegment(
     !flushingPartialBoundaries &&
     isEligibleForOutlining(request, boundary) &&
     (flushedByteSize + boundary.byteSize > request.progressiveChunkSize ||
-      hasSuspenseyContent(boundary.contentState) ||
+      hasSuspenseyContent(boundary.contentState, flushingShell) ||
       boundary.defer)
   ) {
     // Inlining this boundary would make the current sequence being written too large
@@ -5826,6 +5826,7 @@ function flushPartiallyCompletedSegment(
 }

 let flushingPartialBoundaries = false;
+let flushingShell = false;

 function flushCompletedQueues(
   request: Request,
@@ -5885,7 +5886,9 @@ function flushCompletedQueues(
         completedPreambleSegments,
         skipBlockingShell,
       );
+      flushingShell = true;
       flushSegment(request, destination, completedRootSegment, null);
+      flushingShell = false;
       request.completedRootSegment = null;
       const isComplete =
         request.allPendingTasks === 0 &&

PATCH

echo "Patch applied successfully."
