#!/bin/bash
set -e

cd /workspace/router

# Check if already patched
grep -q "prevLoadPromise = undefined" packages/router-core/src/load-matches.ts && {
    echo "Patch already applied, skipping"
    exit 0
}

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/router-core/src/load-matches.ts b/packages/router-core/src/load-matches.ts
index bd04f00481e..6b400833fae 100644
--- a/packages/router-core/src/load-matches.ts
+++ b/packages/router-core/src/load-matches.ts
@@ -391,9 +391,10 @@ const executeBeforeLoad = (
   const match = inner.router.getMatch(matchId)!

   // explicitly capture the previous loadPromise
-  const prevLoadPromise = match._nonReactive.loadPromise
+  let prevLoadPromise = match._nonReactive.loadPromise
   match._nonReactive.loadPromise = createControlledPromise<void>(() => {
     prevLoadPromise?.resolve()
+    prevLoadPromise = undefined
   })

   const { paramsError, searchError } = match
@@ -835,6 +836,7 @@ const loadRouteMatch = async (
           match._nonReactive.loaderPromise?.resolve()
           match._nonReactive.loadPromise?.resolve()
           match._nonReactive.loaderPromise = undefined
+          match._nonReactive.loadPromise = undefined
         } catch (err) {
           if (isRedirect(err)) {
             await inner.router.navigate(err.options)
@@ -926,6 +928,7 @@ const loadRouteMatch = async (
   if (!loaderIsRunningAsync) {
     match._nonReactive.loaderPromise?.resolve()
     match._nonReactive.loadPromise?.resolve()
+    match._nonReactive.loadPromise = undefined
   }

   clearTimeout(match._nonReactive.pendingTimeout)
diff --git a/packages/router-core/src/router.ts b/packages/router-core/src/router.ts
index 3f79a151d94..117a591ca7e 100644
--- a/packages/router-core/src/router.ts
+++ b/packages/router-core/src/router.ts
@@ -2120,9 +2120,10 @@ export class RouterCore<
     const isSameUrl =
       trimPathRight(this.latestLocation.href) === trimPathRight(next.href)

-    const previousCommitPromise = this.commitLocationPromise
+    let previousCommitPromise = this.commitLocationPromise
     this.commitLocationPromise = createControlledPromise<void>(() => {
       previousCommitPromise?.resolve()
+      previousCommitPromise = undefined
     })

     // Don't commit to history if nothing changed
PATCH

# Rebuild the package to apply changes
pnpm nx run @tanstack/router-core:build

echo "Patch applied successfully"
