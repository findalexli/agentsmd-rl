#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if the fix is already applied (idempotency check)
if grep -q "ownerDocument.activeElement === element" packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the gold patch to fix focus handling in Fragment refs
git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
index 4cb4e8e4273a..727ec694bbf7 100644
--- a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
+++ b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
@@ -4520,18 +4520,30 @@ export function setFocusIfFocusable(
   //
   // We could compare the node to document.activeElement after focus,
   // but this would not handle the case where application code managed focus to automatically blur.
+  const element = ((node: any): HTMLElement);
+
+  // If this element is already the active element, it's focusable and already
+  // focused. Calling .focus() on it would be a no-op (no focus event fires),
+  // so we short-circuit here.
+  if (element.ownerDocument.activeElement === element) {
+    return true;
+  }
+
   let didFocus = false;
   const handleFocus = () => {
     didFocus = true;
   };

-  const element = ((node: any): HTMLElement);
   try {
-    element.addEventListener('focus', handleFocus);
+    // Listen on the document in the capture phase so we detect focus even when
+    // it lands on a different element than the one we called .focus() on. This
+    // happens with <label> elements (focus delegates to the associated input)
+    // and shadow hosts with delegatesFocus.
+    element.ownerDocument.addEventListener('focus', handleFocus, true);
     // $FlowFixMe[method-unbinding]
     (element.focus || HTMLElement.prototype.focus).call(element, focusOptions);
   } finally {
-    element.removeEventListener('focus', handleFocus);
+    element.ownerDocument.removeEventListener('focus', handleFocus, true);
   }

   return didFocus;
PATCH

echo "Focus handling fix applied successfully"
