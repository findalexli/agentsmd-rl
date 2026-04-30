#!/bin/bash
# Apply the gold patch from astral-sh/ruff#24661 and rebuild ty.
set -euo pipefail

cd /workspace/ruff

# Idempotency: the new comment introduced by the patch is unique enough.
if grep -q "We could similarly perform multi-inference here if there are multiple overloads" \
        crates/ty_python_semantic/src/types/infer/builder.rs 2>/dev/null; then
    echo "Patch already applied; skipping."
else
    git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/bidirectional.md b/crates/ty_python_semantic/resources/mdtest/bidirectional.md
index c033b4639871d..5fee3d0efb209 100644
--- a/crates/ty_python_semantic/resources/mdtest/bidirectional.md
+++ b/crates/ty_python_semantic/resources/mdtest/bidirectional.md
@@ -505,6 +505,16 @@ reveal_type(f7)  # revealed: (int, /) -> None
 # TODO: This should reveal `(*args: int, *, x=1) -> None` once we support `Unpack`.
 f8: Callable[[*tuple[int, ...], int], None] = lambda *args, x=1: None
 reveal_type(f8)  # revealed: (*args, *, x=1) -> None
+
+def _(x: bool):
+    signatures = {
+        "upper": str.upper,
+        "lower": str.lower,
+        "title": str.title,
+    }
+
+    # revealed: (x) -> Unknown
+    f = signatures.get("", reveal_type(lambda x: x))
 ```

 We do not currently account for type annotations present later in the scope:
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 3c0fb34949b67..9e929d439a51c 100644
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
fi

# Rebuild the ty binary so subsequent test invocations pick up the fix.
cargo build --bin ty
