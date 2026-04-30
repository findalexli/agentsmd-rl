#!/bin/bash
set -e

cd /workspace/sui

# Idempotency check: if already patched, exit successfully
if grep -q "NUMBER_OF_ARGUMENTS_MISMATCH" external-crates/move/crates/move-vm-runtime/src/execution/vm.rs 2>/dev/null; then
    echo "Patch already applied, exiting"
    exit 0
fi

# Apply the gold patch
patch_file=$(mktemp)
cat > "$patch_file" << 'PATCH_EOF'
diff --git a/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs b/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
index 31748a70002f8..f701fef740ddf 100644
--- a/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
+++ b/external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
@@ -351,6 +351,28 @@ impl<'extensions> MoveVM<'extensions> {
                     return_type: _,
                 } = self.find_function(original_id, function_name, &type_arguments)?;

+                if args.len() != function.to_ref().parameters.len() {
+                    return Err(partial_vm_error!(
+                        NUMBER_OF_ARGUMENTS_MISMATCH,
+                        "argument length mismatch: expected {} got {}",
+                        function.to_ref().parameters.len(),
+                        args.len(),
+                    )
+                    .finish(Location::Module(function.module_id(&self.interner))));
+                }
+
+                // Internal type error if we get here -- `find_function` should have already
+                // verified the type arguments as part of the type resolution that it performs.
+                if type_arguments.len() != function.to_ref().type_parameters().len() {
+                    return Err(partial_vm_error!(
+                        INTERNAL_TYPE_ERROR,
+                        "type argument length mismatch: expected {} got {}.",
+                        function.to_ref().type_parameters().len(),
+                        type_arguments.len(),
+                    )
+                    .finish(Location::Module(function.module_id(&self.interner))));
+                }
+
                 if !bypass_declared_entry_check && !function.to_ref().is_entry {
                     return Err(partial_vm_error!(EXECUTE_ENTRY_FUNCTION_CALLED_ON_NON_ENTRY_FUNCTION)
                     .finish(Location::Module(function.module_id(&self.interner))));
diff --git a/external-crates/move/crates/move-vm-runtime/src/unit_tests/function_arg_tests.rs b/external-crates/move/crates/move-vm-runtime/src/unit_tests/function_arg_tests.rs
index f1f492f75b8ab..203e92889e2ad 100644
--- a/external-crates/move/crates/move-vm-runtime/src/unit_tests/function_arg_tests.rs
+++ b/external-crates/move/crates/move-vm-runtime/src/unit_tests/function_arg_tests.rs
@@ -7,9 +7,9 @@ use crate::{
         compilation_utils::{as_module, compile_units},
         in_memory_test_adapter::InMemoryTestAdapter,
         storage::StoredPackage,
-        vm_arguments::ValueFrame,
         vm_test_adapter::VMTestAdapter,
     },
+    execution::{interpreter::locals::BaseHeap, values::Value},
     shared::gas::UnmeteredGasMeter,
 };
 use move_binary_format::errors::VMResult;
@@ -17,7 +17,6 @@ use move_core_types::{
     account_address::AccountAddress,
     identifier::Identifier,
     language_storage::{ModuleId, TypeTag},
-    runtime_value::{MoveStruct, MoveValue},
     u256::U256,
     vm_status::StatusCode,
 };
@@ -28,7 +27,7 @@ fn run(
     ty_params: &[&str],
     params: &[&str],
     ty_arg_tags: Vec<TypeTag>,
-    args: Vec<MoveValue>,
+    args: Vec<Value>,
 ) -> VMResult<()> {
     let ty_params = ty_params
         .iter()
@@ -72,31 +71,31 @@ fn run(
         .map(|tag| sess.load_type(&tag))
         .collect::<VMResult<_>>()?;

-    ValueFrame::serialized_call(
-        &mut sess,
+    sess.execute_function_bypass_visibility(
         &module_id,
         &fun_name,
         ty_args,
-        args.into_iter()
-            .map(|v| v.simple_serialize().unwrap())
-            .collect(),
+        args,
         &mut UnmeteredGasMeter,
         None,
-        true,
     )?;

     Ok(())
 }

-fn expect_err(params: &[&str], args: Vec<MoveValue>, expected_status: StatusCode) {
+fn expect_err(params: &[&str], args: Vec<Value>, expected_status: StatusCode) {
     assert!(run(&[], params, vec![], args).unwrap_err().major_status() == expected_status);
 }

+fn expect_ok(params: &[&str], args: Vec<Value>) {
+    run(&[], params, vec![], args).unwrap()
+}
+
 fn expect_err_generic(
     ty_params: &[&str],
     params: &[&str],
     ty_args: Vec<TypeTag>,
-    args: Vec<MoveValue>,
+    args: Vec<Value>,
     expected_status: StatusCode,
 ) {
     assert!(
@@ -107,17 +106,14 @@ fn expect_err_generic(
     );
 }

-fn expect_ok(params: &[&str], args: Vec<MoveValue>) {
-    run(&[], params, vec![], args).unwrap()
+fn expect_ok_generic(ty_params: &[&str], params: &[&str], ty_args: Vec<TypeTag>, args: Vec<Value>) {
+    run(ty_params, params, ty_args, args).unwrap()
 }

-fn expect_ok_generic(
-    ty_params: &[&str],
-    params: &[&str],
-    ty_args: Vec<TypeTag>,
-    args: Vec<MoveValue>,
-) {
-    run(ty_params, params, ty_args, args).unwrap()
+/// Helper: wrap a `Value` in an immutable reference via a `BaseHeap`.
+fn make_ref(heap: &mut BaseHeap, value: Value) -> Value {
+    let (_id, ref_val) = heap.allocate_and_borrow_loc(value).unwrap();
+    ref_val
 }

 #[test]
@@ -129,7 +125,7 @@ fn expected_0_args_got_0() {
 fn expected_0_args_got_1() {
     expect_err(
         &[],
-        vec![MoveValue::U64(0)],
+        vec![Value::u64(0)],
         StatusCode::NUMBER_OF_ARGUMENTS_MISMATCH,
     )
 }
@@ -143,7 +139,7 @@ fn expected_1_arg_got_0() {
 fn expected_2_arg_got_1() {
     expect_err(
         &["u64", "bool"],
-        vec![MoveValue::U64(0)],
+        vec![Value::u64(0)],
         StatusCode::NUMBER_OF_ARGUMENTS_MISMATCH,
     )
 }
@@ -152,60 +148,47 @@ fn expected_2_arg_got_1() {
 fn expected_2_arg_got_3() {
     expect_err(
         &["u64", "bool"],
-        vec![
-            MoveValue::U64(0),
-            MoveValue::Bool(true),
-            MoveValue::Bool(false),
-        ],
+        vec![Value::u64(0), Value::bool(true), Value::bool(false)],
         StatusCode::NUMBER_OF_ARGUMENTS_MISMATCH,
     )
 }

 #[test]
 fn expected_u64_got_u64() {
-    expect_ok(&["u64"], vec![MoveValue::U64(0)])
+    expect_ok(&["u64"], vec![Value::u64(0)])
 }

 #[test]
 #[allow(non_snake_case)]
 fn expected_Foo_got_Foo() {
-    expect_ok(
-        &["Foo"],
-        vec![MoveValue::Struct(MoveStruct::new(vec![MoveValue::U64(0)]))],
-    )
+    expect_ok(&["Foo"], vec![Value::make_struct(vec![Value::u64(0)])])
 }

 #[test]
 fn expected_signer_ref_got_signer() {
-    expect_ok(&["&signer"], vec![MoveValue::Signer(TEST_ADDR)])
+    let mut heap = BaseHeap::new();
+    let signer_ref = make_ref(&mut heap, Value::signer(TEST_ADDR));
+    expect_ok(&["&signer"], vec![signer_ref])
 }

 #[test]
 fn expected_u64_signer_ref_got_u64_signer() {
-    expect_ok(
-        &["u64", "&signer"],
-        vec![MoveValue::U64(0), MoveValue::Signer(TEST_ADDR)],
-    )
-}
-
-#[test]
-fn expected_u64_got_bool() {
-    expect_err(
-        &["u64"],
-        vec![MoveValue::Bool(false)],
-        StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
-    )
+    let mut heap = BaseHeap::new();
+    let signer_ref = make_ref(&mut heap, Value::signer(TEST_ADDR));
+    expect_ok(&["u64", "&signer"], vec![Value::u64(0), signer_ref])
 }

 #[test]
 fn param_type_u64_ref() {
-    expect_ok(&["&u64"], vec![MoveValue::U64(0)])
+    let mut heap = BaseHeap::new();
+    let u64_ref = make_ref(&mut heap, Value::u64(0));
+    expect_ok(&["&u64"], vec![u64_ref])
 }

 #[test]
 #[allow(non_snake_case)]
 fn expected_T__T_got_u64__u64() {
-    expect_ok_generic(&["T"], &["T"], vec![TypeTag::U64], vec![MoveValue::U64(0)])
+    expect_ok_generic(&["T"], &["T"], vec![TypeTag::U64], vec![Value::u64(0)])
 }

 #[test]
@@ -215,11 +198,7 @@ fn expected_A_B__A_u64_vector_B_got_u8_u128__u8_u64_vector_u128() {
         &["A", "B"],
         &["A", "u64", "vector<B>"],
         vec![TypeTag::U8, TypeTag::U128],
-        vec![
-            MoveValue::U8(0),
-            MoveValue::U64(0),
-            MoveValue::Vector(vec![MoveValue::U128(0), MoveValue::U128(0)]),
-        ],
+        vec![Value::u8(0), Value::u64(0), Value::vector_u128(vec![0, 0])],
     )
 }

@@ -231,12 +210,9 @@ fn expected_A_B__A_u32_vector_B_got_u16_u256__u16_u32_vector_u256() {
         &["A", "u32", "vector<B>"],
         vec![TypeTag::U16, TypeTag::U256],
         vec![
-            MoveValue::U16(0),
-            MoveValue::U32(0),
-            MoveValue::Vector(vec![
-                MoveValue::U256(U256::from(0u8)),
-                MoveValue::U256(U256::from(0u8)),
-            ]),
+            Value::u16(0),
+            Value::u32(0),
+            Value::vector_u256(vec![U256::from(0u8), U256::from(0u8)]),
         ],
     )
 }
@@ -248,9 +224,7 @@ fn expected_T__Bar_T_got_bool__Bar_bool() {
         &["T"],
         &["Bar<T>"],
         vec![TypeTag::Bool],
-        vec![MoveValue::Struct(MoveStruct::new(vec![MoveValue::Bool(
-            false,
-        )]))],
+        vec![Value::make_struct(vec![Value::bool(false)])],
     )
 }

@@ -261,36 +235,69 @@ fn expected_T__T_got_bool__bool() {
         &["T"],
         &["T"],
         vec![TypeTag::Bool],
-        vec![MoveValue::Bool(false)],
+        vec![Value::bool(false)],
     )
 }

 #[test]
 #[allow(non_snake_case)]
-fn expected_T__T_got_bool__u64() {
+fn expected_T__T_ref_got_u64__u64() {
+    let mut heap = BaseHeap::new();
+    let u64_ref = make_ref(&mut heap, Value::u64(0));
+    expect_ok_generic(&["T"], &["&T"], vec![TypeTag::U64], vec![u64_ref])
+}
+
+#[test]
+fn expected_1_ty_arg_got_0() {
     expect_err_generic(
         &["T"],
         &["T"],
-        vec![TypeTag::Bool],
-        vec![MoveValue::U64(0)],
-        StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
+        vec![],
+        vec![Value::u64(0)],
+        StatusCode::NUMBER_OF_TYPE_ARGUMENTS_MISMATCH,
     )
 }

 #[test]
-#[allow(non_snake_case)]
-fn expected_T__T_ref_got_u64__u64() {
-    expect_ok_generic(&["T"], &["&T"], vec![TypeTag::U64], vec![MoveValue::U64(0)])
+fn expected_1_ty_arg_got_2() {
+    expect_err_generic(
+        &["T"],
+        &["T"],
+        vec![TypeTag::U64, TypeTag::Bool],
+        vec![Value::u64(0)],
+        StatusCode::NUMBER_OF_TYPE_ARGUMENTS_MISMATCH,
+    )
 }

 #[test]
-#[allow(non_snake_case)]
-fn expected_T__Bar_T_got_bool__Bar_u64() {
+fn expected_0_ty_args_got_1() {
     expect_err_generic(
-        &["T"],
-        &["Bar<T>"],
-        vec![TypeTag::Bool],
-        vec![MoveValue::Struct(MoveStruct::new(vec![MoveValue::U64(0)]))],
-        StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
+        &[],
+        &["u64"],
+        vec![TypeTag::U64],
+        vec![Value::u64(0)],
+        StatusCode::NUMBER_OF_TYPE_ARGUMENTS_MISMATCH,
+    )
+}
+
+#[test]
+fn expected_2_ty_args_got_1() {
+    expect_err_generic(
+        &["A", "B"],
+        &["A", "B"],
+        vec![TypeTag::U64],
+        vec![Value::u64(0), Value::bool(false)],
+        StatusCode::NUMBER_OF_TYPE_ARGUMENTS_MISMATCH,
+    )
+}
+
+#[test]
+fn expected_2_ty_args_got_3() {
+    expect_err_generic(
+        &["A", "B"],
+        &["A", "B"],
+        vec![TypeTag::U64, TypeTag::Bool, TypeTag::U8],
+        vec![Value::u64(0), Value::bool(false)],
+        StatusCode::NUMBER_OF_TYPE_ARGUMENTS_MISMATCH,
     )
 }
PATCH_EOF

git apply "$patch_file"
rm "$patch_file"

echo "Patch applied successfully"
