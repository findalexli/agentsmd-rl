#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'UnpackedTypedDictKey' crates/ty_python_semantic/src/types/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index fa63ef7d7f125..1aa8fb330321f 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -689,6 +689,22 @@ def copy_person_positional(p: PersonBase) -> PersonAlias:
     return PersonAlias(p)
 ```

+Optional source keys should not satisfy required constructor keys when unpacking:
+
+```py
+from typing import TypedDict
+
+class MaybeName(TypedDict, total=False):
+    name: str
+
+class NeedsName(TypedDict):
+    name: str
+
+def f(maybe: MaybeName) -> NeedsName:
+    # error: [missing-typed-dict-key] "Missing required key 'name' in TypedDict `NeedsName` constructor"
+    return NeedsName(**maybe)
+```
+
 Unpacking a TypedDict with extra keys flags the extra keys as errors, for consistency with the
 behavior when passing all keys as explicit keyword arguments:

diff --git a/crates/ty_python_semantic/src/types/class.rs b/crates/ty_python_semantic/src/types/class.rs
index 278f812ec8edc..1ea072e3ac81f 100644
--- a/crates/ty_python_semantic/src/types/class.rs
+++ b/crates/ty_python_semantic/src/types/class.rs
@@ -34,7 +34,7 @@ use crate::types::signatures::{CallableSignature, Parameter, Parameters, Signatu
 use crate::types::tuple::TupleSpec;
 use crate::types::{
     ApplyTypeMappingVisitor, CallableType, CallableTypes, DataclassParams,
-    FindLegacyTypeVarsVisitor, IntersectionBuilder, TypeContext, TypeMapping, UnionBuilder,
+    FindLegacyTypeVarsVisitor, IntersectionType, TypeContext, TypeMapping, UnionBuilder,
     VarianceInferable,
 };
 use crate::{
@@ -2346,13 +2346,8 @@ impl<'db> CompletedMemberLookup<'db> {
                     qualifiers,
                 },
                 Some(dynamic),
-            ) => Place::bound(
-                IntersectionBuilder::new(db)
-                    .add_positive(ty)
-                    .add_positive(dynamic)
-                    .build(),
-            )
-            .with_qualifiers(qualifiers),
+            ) => Place::bound(IntersectionType::from_two_elements(db, ty, dynamic))
+                .with_qualifiers(qualifiers),

             (
                 PlaceAndQualifiers {
diff --git a/crates/ty_python_semantic/src/types/typed_dict.rs b/crates/ty_python_semantic/src/types/typed_dict.rs
index 4322f4f012563..acae24520966b 100644
--- a/crates/ty_python_semantic/src/types/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/typed_dict.rs
@@ -18,7 +18,7 @@ use super::diagnostic::{
 };
 use super::infer::infer_deferred_types;
 use super::{
-    ApplyTypeMappingVisitor, IntersectionBuilder, Type, TypeMapping, TypeQualifiers,
+    ApplyTypeMappingVisitor, IntersectionType, Type, TypeMapping, TypeQualifiers,
     definition_expression_type, visitor,
 };
 use crate::Db;
@@ -816,22 +816,37 @@ pub(super) fn validate_typed_dict_required_keys<'db, 'ast>(
     !has_missing_key
 }

-/// Extracts `TypedDict` keys and their types from a type, resolving type aliases and handling
-/// intersections.
+#[derive(Debug, Clone, Copy)]
+struct UnpackedTypedDictKey<'db> {
+    value_ty: Type<'db>,
+    is_required: bool,
+}
+
+/// Extracts `TypedDict` keys, their value types, and whether they are required when unpacked as
+/// `**kwargs`, resolving type aliases and handling intersections.
 ///
-/// For intersections, returns ALL keys from ALL `TypedDict` types (union of keys), because a
-/// value of an intersection type must satisfy all `TypedDict`s and therefore has all their keys.
-/// For keys that appear in multiple `TypedDict`s, the types are intersected.
-fn extract_typed_dict_keys<'db>(
+/// For intersections, returns ALL declared keys from ALL `TypedDict` types (union of keys),
+/// because unpacking a value of an intersection type may expose any key declared by any
+/// constituent `TypedDict`. For keys that appear in multiple `TypedDict`s, the value types are
+/// intersected, and the key is considered required if any constituent `TypedDict` requires it.
+fn extract_unpacked_typed_dict_keys<'db>(
     db: &'db dyn Db,
     ty: Type<'db>,
-) -> Option<BTreeMap<Name, Type<'db>>> {
+) -> Option<BTreeMap<Name, UnpackedTypedDictKey<'db>>> {
     match ty {
         Type::TypedDict(td) => {
             let keys = td
                 .items(db)
                 .iter()
-                .map(|(name, field)| (name.clone(), field.declared_ty))
+                .map(|(name, field)| {
+                    (
+                        name.clone(),
+                        UnpackedTypedDictKey {
+                            value_ty: field.declared_ty,
+                            is_required: field.is_required(),
+                        },
+                    )
+                })
                 .collect();
             Some(keys)
         }
@@ -840,28 +855,29 @@ fn extract_typed_dict_keys<'db>(
             let all_key_maps: Vec<_> = intersection
                 .positive(db)
                 .iter()
-                .filter_map(|element| extract_typed_dict_keys(db, *element))
+                .filter_map(|element| extract_unpacked_typed_dict_keys(db, *element))
                 .collect();

             if all_key_maps.is_empty() {
                 return None;
             }

-            // Union all keys from all TypedDicts, intersecting types for shared keys
-            let mut result: BTreeMap<Name, Type<'db>> = BTreeMap::new();
+            // Union all keys from all TypedDicts, intersecting value types for shared keys.
+            let mut result: BTreeMap<Name, UnpackedTypedDictKey<'db>> = BTreeMap::new();

             for key_map in all_key_maps {
-                for (key, ty) in key_map {
+                for (key, unpacked_key) in key_map {
                     result
                         .entry(key)
-                        .and_modify(|existing_ty| {
-                            // Key exists in multiple TypedDicts - intersect the types
-                            *existing_ty = IntersectionBuilder::new(db)
-                                .add_positive(*existing_ty)
-                                .add_positive(ty)
-                                .build();
+                        .and_modify(|existing| {
+                            existing.value_ty = IntersectionType::from_two_elements(
+                                db,
+                                existing.value_ty,
+                                unpacked_key.value_ty,
+                            );
+                            existing.is_required |= unpacked_key.is_required;
                         })
-                        .or_insert(ty);
+                        .or_insert(unpacked_key);
                 }
             }

@@ -869,7 +885,7 @@ fn extract_typed_dict_keys<'db>(
         }
         // TODO: handle unions by checking all TypedDict elements separately
         Type::Union(_) => None,
-        Type::TypeAlias(alias) => extract_typed_dict_keys(db, alias.value_type(db)),
+        Type::TypeAlias(alias) => extract_unpacked_typed_dict_keys(db, alias.value_type(db)),
         // All other types cannot contain a TypedDict
         Type::Dynamic(_)
         | Type::Divergent(_)
@@ -1051,15 +1067,18 @@ fn validate_from_keywords<'db, 'ast>(
                         provided_keys.insert(key_name.clone());
                     }
                 }
-            } else if let Some(unpacked_keys) = extract_typed_dict_keys(db, unpacked_type) {
-                for (key_name, value_ty) in &unpacked_keys {
-                    provided_keys.insert(key_name.clone());
+            } else if let Some(unpacked_keys) = extract_unpacked_typed_dict_keys(db, unpacked_type)
+            {
+                for (key_name, unpacked_key) in &unpacked_keys {
+                    if unpacked_key.is_required {
+                        provided_keys.insert(key_name.clone());
+                    }
                     TypedDictKeyAssignment {
                         context,
                         typed_dict,
                         full_object_ty: None,
                         key: key_name.as_str(),
-                        value_ty: *value_ty,
+                        value_ty: unpacked_key.value_ty,
                         typed_dict_node,
                         key_node: keyword.into(),
                         value_node: (&keyword.value).into(),

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
