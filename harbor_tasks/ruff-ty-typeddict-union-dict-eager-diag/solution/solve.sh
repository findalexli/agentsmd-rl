#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: look for the has_dict_compatible_fallback variable added by the fix
if grep -q 'has_dict_compatible_fallback' crates/ty_python_semantic/src/types/infer/builder.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index f0ab061ec9daa..d872ba3697832 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -45,6 +45,21 @@ reveal_type(bob["age"])  # revealed: int | None
 reveal_type(bob["non_existing"])  # revealed: Unknown
 ```

+If a dict literal is inferred against a union containing both a `TypedDict` and a plain `dict`,
+extra keys accepted by the non-`TypedDict` arm should not trigger eager `TypedDict` diagnostics:
+
+```py
+from typing import Any
+
+class FormatterConfig(TypedDict, total=False):
+    format: str
+
+def takes_formatter(config: FormatterConfig | dict[str, Any]) -> None: ...
+
+takes_formatter({"format": "%(message)s"})
+takes_formatter({"factory": object(), "facility": "local0"})
+```
+
 Methods that are available on `dict`s are also available on `TypedDict`s:

 ```py
@@ -514,6 +529,13 @@ class Foo(TypedDict):
 x1: Foo | None = {"foo": 1}
 reveal_type(x1)  # revealed: Foo

+# A union with no dict-compatible fallback should still validate eagerly against the
+# TypedDict arm.
+# error: [missing-typed-dict-key] "Missing required key 'foo' in TypedDict `Foo` constructor"
+# error: [invalid-key] "Unknown key "bar" for TypedDict `Foo`"
+x1_bad: Foo | None = {"bar": 1}
+reveal_type(x1_bad)  # revealed: Foo | None
+
 class Bar(TypedDict):
     bar: int

diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 1ca359fd9e480..c346a20debe3f 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -5789,57 +5789,76 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         let mut item_types = FxHashMap::default();

         // Validate `TypedDict` dictionary literal assignments.
-        if let Some(tcx) = tcx.annotation {
-            let tcx = tcx.filter_union(self.db(), Type::is_typed_dict);
-
-            if let Some(typed_dict) = tcx.as_typed_dict() {
+        if let Some(annotation) = tcx
+            .annotation
+            .map(|annotation| annotation.resolve_type_alias(self.db()))
+        {
+            if let Some(typed_dict) = annotation.as_typed_dict() {
                 // If there is a single typed dict annotation, infer against it directly.
                 if let Some(ty) =
                     self.infer_typed_dict_expression(dict, typed_dict, &mut item_types)
                 {
                     return ty;
                 }
-            } else if let Type::Union(tcx) = tcx {
-                // Otherwise, we have to narrow to specific elements of the union.
-                //
-                // Infer all expressions with diagnostics enabled before starting multi-inference.
-                for item in items {
-                    if let Some(key) = item.key.as_ref() {
-                        let key_ty = self.infer_expression(key, TypeContext::default());
-                        item_types.insert(key.node_index().load(), key_ty);
-                    }
+            } else if let Type::Union(union) = annotation {
+                let union_elements = union.elements(self.db());
+                let typed_dicts = union_elements
+                    .iter()
+                    .filter_map(|element| element.as_typed_dict())
+                    .collect_vec();
+                let has_dict_compatible_fallback = union_elements.iter().any(|element| {
+                    !element.is_typed_dict() && element.is_instance_of(self.db(), KnownClass::Dict)
+                });

-                    let value_ty = self.infer_expression(&item.value, TypeContext::default());
-                    item_types.insert(item.value.node_index().load(), value_ty);
-                }
+                if let [typed_dict] = typed_dicts.as_slice()
+                    && !has_dict_compatible_fallback
+                {
+                    if let Some(ty) =
+                        self.infer_typed_dict_expression(dict, *typed_dict, &mut item_types)
+                    {
+                        return ty;
+                    }
+                } else if !typed_dicts.is_empty() {
+                    // Infer all expressions with diagnostics enabled before starting
+                    // multi-inference. This preserves the general expression types even if we later
+                    // fall back to a non-`TypedDict` arm of the union.
+                    for item in items {
+                        if let Some(key) = item.key.as_ref() {
+                            let key_ty = self.infer_expression(key, TypeContext::default());
+                            item_types.insert(key.node_index().load(), key_ty);
+                        }

-                // Disable diagnostics as we attempt to narrow to specific elements of the union.
-                let old_multi_inference = self.context.set_multi_inference(true);
-                let old_multi_inference_state =
-                    self.set_multi_inference_state(MultiInferenceState::Ignore);
+                        let value_ty = self.infer_expression(&item.value, TypeContext::default());
+                        item_types.insert(item.value.node_index().load(), value_ty);
+                    }

-                let mut narrowed_tys = Vec::new();
-                let mut item_types = FxHashMap::default();
-                for element in tcx.elements(self.db()) {
-                    let typed_dict = element
-                        .as_typed_dict()
-                        .expect("filtered out non-typed-dict types above");
+                    // Disable diagnostics as we attempt to narrow to specific `TypedDict`
+                    // elements of the union. Mixed unions like `TypedDict | dict[str, Any]`
+                    // should not emit `TypedDict` diagnostics if a non-`TypedDict` arm accepts
+                    // the literal.
+                    let old_multi_inference = self.context.set_multi_inference(true);
+                    let old_multi_inference_state =
+                        self.set_multi_inference_state(MultiInferenceState::Ignore);
+
+                    let mut narrowed_tys = Vec::new();
+                    let mut item_types = FxHashMap::default();
+                    for typed_dict in typed_dicts {
+                        if let Some(inferred_ty) =
+                            self.infer_typed_dict_expression(dict, typed_dict, &mut item_types)
+                        {
+                            narrowed_tys.push(inferred_ty);
+                        }

-                    if let Some(inferred_ty) =
-                        self.infer_typed_dict_expression(dict, typed_dict, &mut item_types)
-                    {
-                        narrowed_tys.push(inferred_ty);
+                        item_types.clear();
                     }

-                    item_types.clear();
-                }
-
-                self.context.set_multi_inference(old_multi_inference);
-                self.set_multi_inference_state(old_multi_inference_state);
+                    self.context.set_multi_inference(old_multi_inference);
+                    self.set_multi_inference_state(old_multi_inference_state);

-                // Successfully narrowed to a subset of typed dicts.
-                if !narrowed_tys.is_empty() {
-                    return UnionType::from_elements(self.db(), narrowed_tys);
+                    // Successfully narrowed to a subset of typed dicts.
+                    if !narrowed_tys.is_empty() {
+                        return UnionType::from_elements(self.db(), narrowed_tys);
+                    }
                 }
             }
         }

PATCH

echo "Patch applied successfully."
