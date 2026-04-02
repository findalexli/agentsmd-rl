#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'pop_with_typed_default_sig' crates/ty_python_semantic/src/types/class/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index 246bb956bf4cd7..aef25297c054ed 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -1824,6 +1824,16 @@ def union_get(u: HasX | OptX) -> None:
     reveal_type(u.get("x"))  # revealed: int | None
 ```

+`pop()` also uses the field type as bidirectional context for the default argument:
+
+```py
+class Config(TypedDict, total=False):
+    data: dict[str, int]
+
+def _(c: Config) -> None:
+    reveal_type(c.pop("data", {}))  # revealed: dict[str, int]
+```
+
 Synthesized `pop()` overloads on `TypedDict` unions correctly handle per-arm requiredness:

 ```py
diff --git a/crates/ty_python_semantic/src/types/class/typed_dict.rs b/crates/ty_python_semantic/src/types/class/typed_dict.rs
index f37c844cbd6be2..d856ea73655924 100644
--- a/crates/ty_python_semantic/src/types/class/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/class/typed_dict.rs
@@ -376,6 +376,23 @@ where
             ];
             let pop_sig = Signature::new(Parameters::new(db, pop_parameters), field.declared_ty);

+            // Non-generic overload that accepts the field type as the default,
+            // providing bidirectional inference context for the default argument.
+            let pop_with_typed_default_sig = Signature::new(
+                Parameters::new(
+                    db,
+                    [
+                        Parameter::positional_only(Some(Name::new_static("self")))
+                            .with_annotated_type(instance_ty),
+                        Parameter::positional_only(Some(Name::new_static("key")))
+                            .with_annotated_type(key_type),
+                        Parameter::positional_only(Some(Name::new_static("default")))
+                            .with_annotated_type(field.declared_ty),
+                    ],
+                ),
+                field.declared_ty,
+            );
+
             let t_default = BoundTypeVarInstance::synthetic(
                 db,
                 Name::new_static("T"),
@@ -396,7 +413,7 @@ where
                 UnionType::from_two_elements(db, field.declared_ty, Type::TypeVar(t_default)),
             );

-            [pop_sig, pop_with_default_sig]
+            [pop_sig, pop_with_typed_default_sig, pop_with_default_sig]
         });

     Type::Callable(CallableType::new(

PATCH
