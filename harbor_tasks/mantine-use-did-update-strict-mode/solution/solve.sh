#!/bin/bash
set -e

cd /workspace/mantine

# Idempotency check - verify if fix is already applied
if grep -q "mounted.current = false" packages/@mantine/hooks/src/use-did-update/use-did-update.ts; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the gold patch
cat > /tmp/use-did-update.patch <<'PATCH'
--- a/packages/@mantine/hooks/src/use-did-update/use-did-update.ts
+++ b/packages/@mantine/hooks/src/use-did-update/use-did-update.ts
@@ -3,11 +3,19 @@ import { DependencyList, EffectCallback, useEffect, useRef } from 'react';
 export function useDidUpdate(fn: EffectCallback, dependencies?: DependencyList) {
   const mounted = useRef(false);

+  useEffect(
+    () => () => {
+      mounted.current = false;
+    },
+    []
+  );
+
   useEffect(() => {
     if (mounted.current) {
       return fn();
     }

     mounted.current = true;
+    return undefined;
   }, dependencies);
 }
PATCH

# Apply the patch
git apply /tmp/use-did-update.patch

echo "Patch applied successfully."
