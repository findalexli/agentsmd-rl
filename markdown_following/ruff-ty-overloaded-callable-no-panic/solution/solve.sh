#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

if grep -q 'TODO: We could similarly perform multi-inference here if there are multiple overloads.' \
        crates/ty_python_semantic/src/types/infer/builder.rs; then
    echo "patch already applied" >&2
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 0000000..1111111 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -6257,16 +6257,16 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

         let callable_tcx = if let Some(tcx) = tcx.annotation
             // TODO: We could perform multi-inference here if there are multiple `Callable` annotations
-            // in the union.
+            // in the union/intersection.
             && let Some(callable) = tcx
                 .filter_union(self.db(), Type::is_callable_type)
                 .as_callable()
         {
-            let [signature] = callable.signatures(self.db()).overloads.as_slice() else {
-                panic!("`Callable` type annotations cannot be overloaded");
-            };
-
-            Some(signature)
+            match callable.signatures(self.db()).overloads.as_slice() {
+                [signature] => Some(signature),
+                // TODO: We could similarly perform multi-inference here if there are multiple overloads.
+                _ => None,
+            }
         } else {
             None
         };
PATCH

echo "solve.sh applied gold patch" >&2
