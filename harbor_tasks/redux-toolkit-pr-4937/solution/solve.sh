#!/bin/bash
set -e

cd /workspace/redux-toolkit

# Apply the gold patch
git apply <<'PATCH'
From: Ben Durrant <ben.durrant@marketdojo.com>
Date: Wed, 9 Apr 2025 11:36:06 +0100
Subject: [PATCH 1/2] improve stability of useInfiniteQuerySubscription's return value

---
 packages/toolkit/src/query/react/buildHooks.ts | 27 +++++++++++++++++++++++---
 1 file changed, 24 insertions(+), 3 deletions(-)

diff --git a/packages/toolkit/src/query/react/buildHooks.ts b/packages/toolkit/src/query/react/buildHooks.ts
index 86ee665d82..d8ad641c4c 100644
--- a/packages/toolkit/src/query/react/buildHooks.ts
+++ b/packages/toolkit/src/query/react/buildHooks.ts
@@ -2052,13 +2052,25 @@ export function buildHooks<Definitions extends EndpointDefinitions>({

       usePromiseRefUnsubscribeOnUnmount(promiseRef)

+      const stableArg = useStableQueryArgs(
+        options.skip ? skipToken : arg,
+        // Even if the user provided a per-endpoint `serializeQueryArgs` with
+        // a consistent return value, _here_ we want to use the default behavior
+        // so we can tell if _anything_ actually changed. Otherwise, we can end up
+        // with a case where the query args did change but the serialization doesn't,
+        // and then we never try to initiate a refetch.
+        defaultSerializeQueryArgs,
+        context.endpointDefinitions[endpointName],
+        endpointName,
+      )
+
       return useMemo(() => {
         const fetchNextPage = () => {
-          return trigger(arg, 'forward')
+          return trigger(stableArg, 'forward')
         }

         const fetchPreviousPage = () => {
-          return trigger(arg, 'backward')
+          return trigger(stableArg, 'backward')
         }

         return {
@@ -2070,7 +2082,7 @@ export function buildHooks<Definitions extends EndpointDefinitions>({
           fetchNextPage,
           fetchPreviousPage,
         }
-      }, [promiseRef, trigger, arg])
+      }, [promiseRef, trigger, stableArg])
     }

     const useInfiniteQueryState: UseInfiniteQueryState<any> =

From: Mark Erikson <mark@isquaredsoftware.com>
Date: Sat, 12 Apr 2025 17:39:51 -0400
Subject: [PATCH 2/2] Ensure refetch is stable

---
 packages/toolkit/src/query/react/buildHooks.ts | 9 +++++++--
 1 file changed, 7 insertions(+), 2 deletions(-)

diff --git a/packages/toolkit/src/query/react/buildHooks.ts b/packages/toolkit/src/query/react/buildHooks.ts
index d8ad641c4c..4450bd593b4 100644
--- a/packages/toolkit/src/query/react/buildHooks.ts
+++ b/packages/toolkit/src/query/react/buildHooks.ts
@@ -2064,6 +2064,11 @@ export function buildHooks<Definitions extends EndpointDefinitions>({
         endpointName,
       )

+      const refetch = useCallback(
+        () => refetchOrErrorIfUnmounted(promiseRef),
+        [promiseRef],
+      )
+
       return useMemo(() => {
         const fetchNextPage = () => {
           return trigger(stableArg, 'forward')
@@ -2078,11 +2083,11 @@ export function buildHooks<Definitions extends EndpointDefinitions>({
           /**
            * A method to manually refetch data for the query
            */
-          refetch: () => refetchOrErrorIfUnmounted(promiseRef),
+          refetch,
           fetchNextPage,
           fetchPreviousPage,
         }
-      }, [promiseRef, trigger, stableArg])
+      }, [refetch, trigger, stableArg])
     }

     const useInfiniteQueryState: UseInfiniteQueryState<any> =
PATCH

# Verify the patch was applied by checking for distinctive line
grep -q "const stableArg = useStableQueryArgs" packages/toolkit/src/query/react/buildHooks.ts
