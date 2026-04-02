#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
if grep -q "function bruteForceFlushErrorsAndWarnings(root: FiberInstance)" packages/react-devtools-shared/src/backend/fiber/renderer.js; then
    echo "Patch already applied"
    exit 0
fi

# Apply the fix for React DevTools commit tree builder root ID issue
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 289bad6f329b..bc1b2a590d59 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -1138,7 +1138,7 @@ export function attach(
   // if any passive effects called console.warn / console.error.
   let needsToFlushComponentLogs = false;

-  function bruteForceFlushErrorsAndWarnings() {
+  function bruteForceFlushErrorsAndWarnings(root: FiberInstance) {
     // Refresh error/warning count for all mounted unfiltered Fibers.
     let hasChanges = false;
     // eslint-disable-next-line no-for-of-loops/no-for-of-loops
@@ -1156,7 +1156,7 @@ export function attach(
       }
     }
     if (hasChanges) {
-      flushPendingEvents();
+      flushPendingEvents(root);
     }
   }

@@ -1183,7 +1183,7 @@ export function attach(
         updateMostRecentlyInspectedElementIfNecessary(devtoolsInstance.id);
       }
     }
-    flushPendingEvents();
+    flushPendingEvents(null);
   }

   function clearConsoleLogsHelper(instanceID: number, type: 'error' | 'warn') {
@@ -1211,7 +1211,7 @@ export function attach(
         }
         const changed = recordConsoleLogs(devtoolsInstance, componentLogsEntry);
         if (changed) {
-          flushPendingEvents();
+          flushPendingEvents(null);
           updateMostRecentlyInspectedElementIfNecessary(devtoolsInstance.id);
         }
       }
@@ -1533,6 +1533,8 @@ export function attach(
     if (isProfiling) {
       // Re-mounting a tree while profiling is in progress might break a lot of assumptions.
       // If necessary, we could support this- but it doesn't seem like a necessary use case.
+      // Supporting change of filters while profiling would require a refactor
+      // to flush after each root instead of at the end.
       throw Error('Cannot modify filter preferences while profiling');
     }

@@ -1647,7 +1649,8 @@ export function attach(
       focusedActivityFilter.activityID = focusedActivityID;
     }

-    flushPendingEvents();
+    // We're not profiling so it's safe to flush without a specific root.
+    flushPendingEvents(null);

     needsToFlushComponentLogs = false;
   }
@@ -2203,7 +2206,12 @@ export function attach(
     }
   }

-  function flushPendingEvents(): void {
+  /**
+   * Allowed to flush pending events without a specific root when:
+   * - pending operations don't record tree mutations e.g. TREE_OPERATION_UPDATE_ERRORS_OR_WARNINGS
+   * - not profiling (the commit tree builder requires the root of the mutations)
+   */
+  function flushPendingEvents(root: FiberInstance | null): void {
     if (shouldBailoutWithPendingOperations()) {
       // If we aren't profiling, we can just bail out here.
       // No use sending an empty update over the bridge.
@@ -2245,11 +2253,10 @@ export function attach(
     // Which in turn enables fiber props, states, and hooks to be inspected.
     let i = 0;
     operations[i++] = rendererID;
-    if (currentRoot === null) {
-      // TODO: This is not always safe so this field is probably not needed.
+    if (root === null) {
       operations[i++] = -1;
     } else {
-      operations[i++] = currentRoot.id;
+      operations[i++] = root.id;
     }

     // Now fill in the string table.
@@ -5746,11 +5753,11 @@ export function attach(

         mountFiberRecursively(root.current, false);

+        flushPendingEvents(currentRoot);
+
         currentRoot = (null: any);
       });

-      flushPendingEvents();
-
       needsToFlushComponentLogs = false;
     }
   }
@@ -5760,7 +5767,7 @@ export function attach(
     // safe to stop calling it from Fiber.
   }

-  function handlePostCommitFiberRoot(root: any) {
+  function handlePostCommitFiberRoot(root: FiberRoot) {
     if (isProfiling && rootSupportsProfiling(root)) {
       if (currentCommitProfilingMetadata !== null) {
         const {effectDuration, passiveEffectDuration} =
@@ -5774,12 +5781,18 @@ export function attach(
     }

     if (needsToFlushComponentLogs) {
+      const rootInstance = rootToFiberInstanceMap.get(root);
+      if (rootInstance === undefined) {
+        throw new Error(
+          'Should have a root instance for a committed root. This is a bug in React DevTools.',
+        );
+      }
       // We received new logs after commit. I.e. in a passive effect. We need to
       // traverse the tree to find the affected ones. If we just moved the whole
       // tree traversal from handleCommitFiberRoot to handlePostCommitFiberRoot
       // this wouldn't be needed. For now we just brute force check all instances.
       // This is not that common of a case.
-      bruteForceFlushErrorsAndWarnings();
+      bruteForceFlushErrorsAndWarnings(rootInstance);
     }
   }

@@ -5876,7 +5889,7 @@ export function attach(
     }

     // We're done here.
-    flushPendingEvents();
+    flushPendingEvents(currentRoot);

     needsToFlushComponentLogs = false;

diff --git a/packages/react-devtools-shared/src/constants.js b/packages/react-devtools-shared/src/constants.js
index c965282e60d6..53488cc2f454 100644
--- a/packages/react-devtools-shared/src/constants.js
+++ b/packages/react-devtools-shared/src/constants.js
@@ -22,7 +22,7 @@ export const TREE_OPERATION_REMOVE = 2;
 export const TREE_OPERATION_REORDER_CHILDREN = 3;
 export const TREE_OPERATION_UPDATE_TREE_BASE_DURATION = 4;
 export const TREE_OPERATION_UPDATE_ERRORS_OR_WARNINGS = 5;
-export const TREE_OPERATION_REMOVE_ROOT = 6;
+// Removed `TREE_OPERATION_REMOVE_ROOT`
 export const TREE_OPERATION_SET_SUBTREE_MODE = 7;
 export const SUSPENSE_TREE_OPERATION_ADD = 8;
 export const SUSPENSE_TREE_OPERATION_REMOVE = 9;
diff --git a/packages/react-devtools-shared/src/devtools/store.js b/packages/react-devtools-shared/src/devtools/store.js
index 3e2dde5fea19..45ced5d4fdd3 100644
--- a/packages/react-devtools-shared/src/devtools/store.js
+++ b/packages/react-devtools-shared/src/devtools/store.js
@@ -16,7 +16,6 @@ import {
   PROFILING_FLAG_PERFORMANCE_TRACKS_SUPPORT,
   TREE_OPERATION_ADD,
   TREE_OPERATION_REMOVE,
-  TREE_OPERATION_REMOVE_ROOT,
   TREE_OPERATION_REORDER_CHILDREN,
   TREE_OPERATION_SET_SUBTREE_MODE,
   TREE_OPERATION_UPDATE_ERRORS_OR_WARNINGS,
@@ -1644,45 +1643,6 @@ export default class Store extends EventEmitter<{

           break;
         }
-        case TREE_OPERATION_REMOVE_ROOT: {
-          i += 1;
-
-          const id = operations[1];
-
-          if (__DEBUG__) {
-            debug(`Remove root ${id}`);
-          }
-
-          const recursivelyDeleteElements = (elementID: number) => {
-            const element = this._idToElement.get(elementID);
-            this._idToElement.delete(elementID);
-            if (element) {
-              // Mostly for Flow's sake
-              for (let index = 0; index < element.children.length; index++) {
-                recursivelyDeleteElements(element.children[index]);
-              }
-            }
-          };
-
-          const root = this._idToElement.get(id);
-          if (root === undefined) {
-            this._throwAndEmitError(
-              Error(
-                `Cannot remove root "${id}": no matching node was found in the Store.`,
-              ),
-            );
-
-            break;
-          }
-
-          recursivelyDeleteElements(id);
-
-          this._rootIDToCapabilities.delete(id);
-          this._rootIDToRendererID.delete(id);
-          this._roots = this._roots.filter(rootID => rootID !== id);
-          this._weightAcrossRoots -= root.weight;
-          break;
-        }
         case TREE_OPERATION_REORDER_CHILDREN: {
           const id = operations[i + 1];
           const numChildren = operations[i + 2];
diff --git a/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js b/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
index 9a2c3fa3056c..02ecc98ec6d1 100644
--- a/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
+++ b/packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js
@@ -11,7 +11,6 @@ import {
   __DEBUG__,
   TREE_OPERATION_ADD,
   TREE_OPERATION_REMOVE,
-  TREE_OPERATION_REMOVE_ROOT,
   TREE_OPERATION_REORDER_CHILDREN,
   TREE_OPERATION_SET_SUBTREE_MODE,
   TREE_OPERATION_UPDATE_TREE_BASE_DURATION,
@@ -313,9 +312,6 @@ function updateTree(
         }
         break;
       }
-      case TREE_OPERATION_REMOVE_ROOT: {
-        throw Error('Operation REMOVE_ROOT is not supported while profiling.');
-      }
       case TREE_OPERATION_REORDER_CHILDREN: {
         id = ((operations[i + 1]: any): number);
         const numChildren = ((operations[i + 2]: any): number);
diff --git a/packages/react-devtools-shared/src/utils.js b/packages/react-devtools-shared/src/utils.js
index c84ed2d36476..66de8440b65e 100644
--- a/packages/react-devtools-shared/src/utils.js
+++ b/packages/react-devtools-shared/src/utils.js
@@ -28,7 +28,6 @@ import {
 import {
   TREE_OPERATION_ADD,
   TREE_OPERATION_REMOVE,
-  TREE_OPERATION_REMOVE_ROOT,
   TREE_OPERATION_REORDER_CHILDREN,
   TREE_OPERATION_SET_SUBTREE_MODE,
   TREE_OPERATION_UPDATE_ERRORS_OR_WARNINGS,
@@ -295,12 +294,6 @@ export function printOperationsArray(operations: Array<number>) {
         }
         break;
       }
-      case TREE_OPERATION_REMOVE_ROOT: {
-        i += 1;
-
-        logs.push(`Remove root ${rootID}`);
-        break;
-      }
       case TREE_OPERATION_SET_SUBTREE_MODE: {
         const id = operations[i + 1];
         const mode = operations[i + 2];
PATCH

echo "Patch applied successfully"
