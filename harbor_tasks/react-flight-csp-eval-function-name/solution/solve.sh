#!/bin/bash
set -euo pipefail

# Apply the fix for React Flight CSP eval function name restoration
# This is the gold patch from PR #35650

# Check if already applied — look for the specific comment added by the patch
# (generic Object.defineProperty exists many times in the base file)
if grep -q "doesn't work here since this will produce" /workspace/react/packages/react-client/src/ReactFlightClient.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
git -C /workspace/react apply - <<'PATCH'
diff --git a/packages/react-client/src/ReactFlightClient.js b/packages/react-client/src/ReactFlightClient.js
index 2246f74697eb..4dc316de3667 100644
--- a/packages/react-client/src/ReactFlightClient.js
+++ b/packages/react-client/src/ReactFlightClient.js
@@ -3730,6 +3730,14 @@ function createFakeFunction<T>(
     fn = function (_) {
       return _();
     };
+    // Using the usual {[name]: _() => _()}.bind() trick to avoid minifiers
+    // doesn't work here since this will produce `Object.*` names.
+    Object.defineProperty(
+      fn,
+      // $FlowFixMe[cannot-write] -- `name` is configurable though.
+      'name',
+      {value: name},
+    );
   }
   return fn;
 }
PATCH

echo "Patch applied successfully"
