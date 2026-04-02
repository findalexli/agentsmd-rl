#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if the typed default overload already exists, skip
if grep -q 'get_with_typed_default_sig' \
    crates/ty_python_semantic/src/types/class/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index 2b3f4954b448bc..6295de11679e5e 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -1742,8 +1742,7 @@ def _(p: Person) -> None:
     reveal_type(p.get("extra", 0))  # revealed: str | Literal[0]

     # Even another typed dict:
-    # TODO: This should evaluate to `Inner`.
-    reveal_type(p.get("inner", {"inner": 0}))  # revealed: Inner | dict[str, int]
+    reveal_type(p.get("inner", {"inner": 0}))  # revealed: Inner

     # We allow access to unknown keys (they could be set for a subtype of Person)
     reveal_type(p.get("unknown"))  # revealed: Unknown | None
@@ -1766,6 +1765,31 @@ def _(p: Person) -> None:
     reveal_type(p.setdefault("extraz", "value"))  # revealed: Unknown
 ```

+Known-key `get()` calls also use the field type as bidirectional context when that produces a valid
+default:
+
+```py
+from typing import TypedDict
+
+class ResolvedData(TypedDict, total=False):
+    x: int
+
+class Payload(TypedDict, total=False):
+    resolved: ResolvedData
+
+class Payload2(TypedDict, total=False):
+    resolved: ResolvedData
+
+def takes_resolved(value: ResolvedData) -> None: ...
+def _(payload: Payload) -> None:
+    reveal_type(payload.get("resolved", {}))  # revealed: ResolvedData
+    takes_resolved(payload.get("resolved", {}))
+
+def _(payload: Payload | Payload2) -> None:
+    reveal_type(payload.get("resolved", {}))  # revealed: ResolvedData
+    takes_resolved(payload.get("resolved", {}))
+```
+
 Synthesized `get()` on unions falls back to generic resolution when a key is missing from one arm:

 ```py
diff --git a/crates/ty_python_semantic/src/types/class/typed_dict.rs b/crates/ty_python_semantic/src/types/class/typed_dict.rs
index 568bdec76a3ed1..1cda560a248162 100644
--- a/crates/ty_python_semantic/src/types/class/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/class/typed_dict.rs
@@ -241,7 +241,29 @@ where
                 },
             );

-            [get_sig, get_with_default_sig]
+            // For non-required fields, add a non-generic overload that accepts the
+            // field type as the default. This is ordered before the generic TypeVar
+            // overload so that `td.get("key", {})` can use the field type as
+            // bidirectional inference context for the default argument.
+            if field.is_required() {
+                vec![get_sig, get_with_default_sig]
+            } else {
+                let get_with_typed_default_sig = Signature::new(
+                    Parameters::new(
+                        db,
+                        [
+                            Parameter::positional_only(Some(Name::new_static("self")))
+                                .with_annotated_type(instance_ty),
+                            Parameter::positional_only(Some(Name::new_static("key")))
+                                .with_annotated_type(key_type),
+                            Parameter::positional_only(Some(Name::new_static("default")))
+                                .with_annotated_type(field.declared_ty),
+                        ],
+                    ),
+                    field.declared_ty,
+                );
+                vec![get_sig, get_with_typed_default_sig, get_with_default_sig]
+            }
         })
         // Fallback overloads for unknown keys
         .chain(std::iter::once(Signature::new(

PATCH

echo "Patch applied successfully."
