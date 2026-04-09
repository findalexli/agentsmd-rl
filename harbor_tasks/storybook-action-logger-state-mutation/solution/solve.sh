#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if grep -q 'slice(-limit)' code/core/src/actions/containers/ActionLogger/index.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/code/core/src/actions/containers/ActionLogger/index.tsx b/code/core/src/actions/containers/ActionLogger/index.tsx
index af1d05b083b2..776842c59cf9 100644
--- a/code/core/src/actions/containers/ActionLogger/index.tsx
+++ b/code/core/src/actions/containers/ActionLogger/index.tsx
@@ -36,15 +36,20 @@ export default function ActionLogger({ active, api }: ActionLoggerProps) {

   const addAction = useCallback((action: ActionDisplay) => {
     setActions((prevActions) => {
-      const newActions = [...prevActions];
-      const previous = newActions.length && newActions[newActions.length - 1];
+      const limit = action.options.limit ?? 50;
+      const previous = prevActions.length ? prevActions[prevActions.length - 1] : null;
+
       if (previous && safeDeepEqual(previous.data, action.data)) {
-        previous.count++;
+        const updated = [...prevActions];
+        updated[updated.length - 1] = {
+          ...previous,
+          count: previous.count + 1,
+        };
+        return updated.slice(-limit);
       } else {
-        action.count = 1;
-        newActions.push(action);
+        const newAction = { ...action, count: 1 };
+        return [...prevActions, newAction].slice(-limit);
       }
-      return newActions.slice(0, action.options.limit);
     });
   }, []);


PATCH

echo "Patch applied successfully."
