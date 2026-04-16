#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if ! grep -q "simple_deserialize" external-crates/move/crates/move-core-types/src/annotated_value.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the patch to remove unused simple_deserialize methods
cat <<'PATCH' | patch -p1
From 3a3ac018177cf71cef28be3f21957b74c6bc45be Mon Sep 17 00:00:00 2001
From: Tim Zakian <tzakian@users.noreply.github.com>
Date: Wed, 8 Apr 2026 11:50:49 -0700
Subject: [move][cleanup] Remove some unused deserialization functions

--- a/crates/sui-analytics-indexer/src/handlers/tables/event.rs
+++ b/crates/sui-analytics-indexer/src/handlers/tables/event.rs
@@ -5,7 +5,6 @@ use std::sync::Arc;

 use anyhow::Result;
 use async_trait::async_trait;
-use move_core_types::annotated_value::MoveValue;
 use sui_indexer_alt_framework::pipeline::Processor;
 use sui_json_rpc_types::type_and_fields_from_move_event_data;
 use sui_types::base_types::EpochId;
@@ -16,6 +15,7 @@ use sui_types::full_checkpoint_content::Checkpoint;
 use sui_package_resolver::PackageStoreWithLruCache;
 use sui_package_resolver::Resolver;
 use sui_rpc_resolver::package_store::RpcPackageStore;
+use sui_types::object::bounded_visitor::BoundedVisitor;

 use crate::Row;
 use crate::pipeline::Pipeline;
@@ -72,7 +72,7 @@ impl Processor for EventProcessor {
                         ))
                         .await?;

-                    let move_value = MoveValue::simple_deserialize(contents, &layout)?;
+                    let move_value = BoundedVisitor::deserialize_value(contents, &layout)?;
                     let (_, event_json) = type_and_fields_from_move_event_data(move_value)?;

                     let row = EventRow {
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
