#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch to remove simple_deserialize methods from annotated_value.rs and runtime_value.rs
cat <<'PATCH' | git apply -
diff --git a/external-crates/move/crates/move-core-types/src/annotated_value.rs b/external-crates/move/crates/move-core-types/src/annotated_value.rs
index a362ab5a2c37..cd513530b173 100644
--- a/external-crates/move/crates/move-core-types/src/annotated_value.rs
+++ b/external-crates/move/crates/move-core-types/src/annotated_value.rs
@@ -11,7 +11,6 @@ use crate::{
     runtime_value::{self as R, MOVE_STRUCT_FIELDS, MOVE_STRUCT_TYPE},
     u256,
 };
-use anyhow::Result as AResult;
 use serde::{
     Deserialize, Serialize,
     de::Error as DeError,
@@ -181,11 +180,6 @@ impl MoveTypeLayout {
 }

 impl MoveValue {
-    /// TODO (annotated-visitor): Port legacy uses of this method to `BoundedVisitor`.
-    pub fn simple_deserialize(blob: &[u8], ty: &MoveTypeLayout) -> AResult<Self> {
-        Ok(bcs::from_bytes_seed(ty, blob)?)
-    }
-
     /// Deserialize `blob` as a Move value with the given `ty`-pe layout, and visit its
     /// sub-structure with the given `visitor`. The visitor dictates the return value that is built
     /// up during deserialization.
@@ -265,11 +259,6 @@ impl MoveStruct {
         Self { type_, fields }
     }

-    /// TODO (annotated-visitor): Port legacy uses of this method to `BoundedVisitor`.
-    pub fn simple_deserialize(blob: &[u8], ty: &MoveStructLayout) -> AResult<Self> {
-        Ok(bcs::from_bytes_seed(ty, blob)?)
-    }
-
     /// Like `MoveValue::visit_deserialize` (see for details), but specialized to visiting a struct
     /// (the `blob` is known to be a serialized Move struct, and the layout is a
     /// `MoveStructLayout`).
@@ -321,10 +310,6 @@ impl MoveVariant {
         }
     }

-    pub fn simple_deserialize(blob: &[u8], ty: &MoveEnumLayout) -> AResult<Self> {
-        Ok(bcs::from_bytes_seed(ty, blob)?)
-    }
-
     pub fn into_fields(self) -> Vec<MoveValue> {
         self.fields.into_iter().map(|(_, v)| v).collect()
     }
diff --git a/external-crates/move/crates/move-core-types/src/runtime_value.rs b/external-crates/move/crates/move-core-types/src/runtime_value.rs
index 5d9bc73d0dc9..b33d53a0489a 100644
--- a/external-crates/move/crates/move-core-types/src/runtime_value.rs
+++ b/external-crates/move/crates/move-core-types/src/runtime_value.rs
@@ -225,10 +225,6 @@ impl MoveStruct {
         Self(value)
     }

-    pub fn simple_deserialize(blob: &[u8], ty: &MoveStructLayout) -> AResult<Self> {
-        Ok(bcs::from_bytes_seed(ty, blob)?)
-    }
-
     /// Like `MoveValue::visit_deserialize` (see for details), but specialized to visiting a struct
     /// (the `blob` is known to be a serialized Move struct, and the layout is a
     /// `MoveStructLayout`).
@@ -278,10 +274,6 @@ impl MoveVariant {
         Self { tag, fields }
     }

-    pub fn simple_deserialize(blob: &[u8], ty: &MoveEnumLayout) -> AResult<Self> {
-        Ok(bcs::from_bytes_seed(ty, blob)?)
-    }
-
     pub fn decorate(self, layout: &A::MoveEnumLayout) -> A::MoveVariant {
         let MoveVariant { tag, fields } = self;
         let A::MoveEnumLayout { type_, variants } = layout;
diff --git a/external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs b/external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs
index a334d36dbaf9..eb7de7df9c49 100644
--- a/external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs
+++ b/external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs
@@ -11,6 +11,10 @@ use crate::{
 };
 use serde_json::json;

+fn deser_annotated_value(blob: &[u8], layout: &A::MoveTypeLayout) -> A::MoveValue {
+    bcs::from_bytes_seed(layout, blob).unwrap()
+}
+
 #[test]
 fn check_layout_size() {
     assert_eq!(std::mem::size_of::<R::MoveTypeLayout>(), 16);
@@ -51,11 +55,10 @@ fn struct_deserialization() {
         .collect(),
     };

-    let deser_typed_value = A::MoveValue::simple_deserialize(
+    let deser_typed_value = deser_annotated_value(
         &ser,
         &A::MoveTypeLayout::Struct(Box::new(struct_type_layout)),
-    )
-    .unwrap();
+    );
     let typed_value = A::MoveStruct::new(struct_type, field_values);

     assert_eq!(
@@ -164,11 +167,10 @@ fn enum_deserialization() {
         json!([1, [8, false, 0]])
     );

-    let deser_typed_value = A::MoveValue::simple_deserialize(
+    let deser_typed_value = deser_annotated_value(
         &ser,
         &A::MoveTypeLayout::Enum(Box::new(enum_type_layout.clone())),
-    )
-    .unwrap();
+    );
     let typed_value = A::MoveVariant {
         type_: enum_type.clone(),
         variant_name: ident_str!("Variant1").to_owned(),
@@ -192,11 +194,8 @@ fn enum_deserialization() {
     let ser1 = R::MoveValue::Variant(runtime_value.clone())
         .simple_serialize()
         .unwrap();
-    let deser1_typed_value = A::MoveValue::simple_deserialize(
-        &ser1,
-        &A::MoveTypeLayout::Enum(Box::new(enum_type_layout)),
-    )
-    .unwrap();
+    let deser1_typed_value =
+        deser_annotated_value(&ser1, &A::MoveTypeLayout::Enum(Box::new(enum_type_layout)));
     let typed_value = A::MoveVariant {
         type_: enum_type,
         variant_name: ident_str!("Variant2").to_owned(),
PATCH

echo "Patch applied successfully"
